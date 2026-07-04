import os
import pytest
import datetime
import database
import auth
import ai_agent
import employee

# Redirect database name to a sandboxed test file to avoid modifying production data
database.DB_NAME = "test_leave_management.db"

@pytest.fixture(autouse=True)
def setup_teardown_db():
    # Set up: Clean up database file if it already exists
    if os.path.exists(database.DB_NAME):
        try:
            os.remove(database.DB_NAME)
        except PermissionError:
            pass
            
    database.init_db()
    
    yield
    
    # Tear down: Clean up database file after test
    if os.path.exists(database.DB_NAME):
        try:
            os.remove(database.DB_NAME)
        except PermissionError:
            pass

def test_leave_form_state_persists_in_session_state():
    """
    Verifies that leave form values are retained in session state so they don't vanish on rerun.
    """
    state = {}
    employee.init_leave_form_state(state)
    state["reason"] = "Need to attend a wedding"
    state["leave_type"] = "Paid"
    state["start_date"] = datetime.date(2026, 8, 1)
    state["end_date"] = datetime.date(2026, 8, 3)

    persisted = employee.init_leave_form_state(state)

    assert persisted["reason"] == "Need to attend a wedding"
    assert persisted["leave_type"] == "Paid"
    assert persisted["start_date"] == datetime.date(2026, 8, 1)
    assert persisted["end_date"] == datetime.date(2026, 8, 3)

    employee.reset_leave_form_state(state)
    assert state["reason"] == ""
    assert state["leave_type"] == "Casual"

def test_database_seeding():
    """
    Verifies that default administrative and employee users are seeded with correct details.
    """
    admin = database.get_user_by_username("admin")
    alice = database.get_user_by_username("alice")
    bob = database.get_user_by_username("bob")
    
    assert admin is not None
    assert admin['role'] == 'admin'
    assert admin['name'] == 'System Administrator'
    
    assert alice is not None
    assert alice['role'] == 'employee'
    assert alice['casual_balance'] == 15
    assert alice['sick_balance'] == 10
    assert alice['paid_balance'] == 20
    
    assert bob is not None
    assert bob['role'] == 'employee'

def test_authentication():
    """
    Verifies that bcrypt hashing, verification, and user authentication works.
    """
    # Test valid credentials
    user = auth.authenticate_user("alice", "password123")
    assert user is not None
    assert user['username'] == 'alice'
    
    # Test case-insensitivity in username login
    user_caps = auth.authenticate_user("ALICE", "password123")
    assert user_caps is not None
    assert user_caps['username'] == 'alice'
    
    # Test invalid credentials
    invalid_user = auth.authenticate_user("alice", "wrongpassword")
    assert invalid_user is None
    
    # Test non-existent user
    non_existent = auth.authenticate_user("nobody", "password123")
    assert non_existent is None

def test_leave_overlap_validation():
    """
    Verifies overlapping date detection logic.
    """
    alice = database.get_user_by_username("alice")
    
    # Apply first leave (July 5 to July 10)
    database.apply_leave(
        user_id=alice['id'],
        leave_type='Casual',
        start_date='2026-07-05',
        end_date='2026-07-10',
        reason='Family trip',
        ai_recommendation='Approve',
        ai_reason='Heuristic auto'
    )
    
    # Test case 1: Perfect match (July 5 to July 10) -> overlap
    overlaps_perfect = database.check_leave_overlap(alice['id'], '2026-07-05', '2026-07-10')
    assert len(overlaps_perfect) > 0
    
    # Test case 2: Inside the range (July 7 to July 8) -> overlap
    overlaps_inside = database.check_leave_overlap(alice['id'], '2026-07-07', '2026-07-08')
    assert len(overlaps_inside) > 0
    
    # Test case 3: Start boundary overlap (July 3 to July 6) -> overlap
    overlaps_start = database.check_leave_overlap(alice['id'], '2026-07-03', '2026-07-06')
    assert len(overlaps_start) > 0
    
    # Test case 4: End boundary overlap (July 9 to July 12) -> overlap
    overlaps_end = database.check_leave_overlap(alice['id'], '2026-07-09', '2026-07-12')
    assert len(overlaps_end) > 0
    
    # Test case 5: Safe range before (July 1 to July 4) -> no overlap
    overlaps_before = database.check_leave_overlap(alice['id'], '2026-07-01', '2026-07-04')
    assert len(overlaps_before) == 0
    
    # Test case 6: Safe range after (July 11 to July 15) -> no overlap
    overlaps_after = database.check_leave_overlap(alice['id'], '2026-07-11', '2026-07-15')
    assert len(overlaps_after) == 0

def test_employee_leave_application_saves_to_database():
    """
    Verifies that a valid employee leave application is saved to SQLite and remains pending.
    """
    alice = database.get_user_by_username("alice")
    initial_requests = database.get_user_leave_requests(alice['id'])
    assert len(initial_requests) == 0

    leave_type = 'Sick'
    start_date = '2026-08-10'
    end_date = '2026-08-12'
    reason = 'Doctor appointment required.'
    duration = 3

    assert duration <= alice['sick_balance']

    rec, rec_reason = ai_agent.analyze_leave_request(
        employee_name=alice['name'],
        leave_type=leave_type,
        duration_days=duration,
        reason=reason,
        remaining_balance=alice['sick_balance']
    )

    database.apply_leave(
        user_id=alice['id'],
        leave_type=leave_type,
        start_date=start_date,
        end_date=end_date,
        reason=reason,
        ai_recommendation=rec,
        ai_reason=rec_reason
    )

    requests = database.get_user_leave_requests(alice['id'])
    assert len(requests) == 1
    saved_request = requests[0]
    assert saved_request['leave_type'] == leave_type
    assert saved_request['start_date'] == start_date
    assert saved_request['end_date'] == end_date
    assert saved_request['reason'] == reason
    assert saved_request['status'] == 'Pending'
    assert saved_request['ai_recommendation'] == rec
    assert saved_request['ai_reason'] == rec_reason

def test_leave_approval_and_balance_deduction():
    """
    Verifies that approving a leave deducts days from the balance and creates audit logs.
    """
    alice = database.get_user_by_username("alice")
    admin = database.get_user_by_username("admin")
    
    # Alice applies for 3 days of Casual leave (July 5 to July 7)
    database.apply_leave(
        user_id=alice['id'],
        leave_type='Casual',
        start_date='2026-07-05',
        end_date='2026-07-07',
        reason='Wedding anniversary',
        ai_recommendation='Approve',
        ai_reason='Heuristic'
    )
    
    requests = database.get_user_leave_requests(alice['id'])
    assert len(requests) == 1
    req = requests[0]
    assert req['status'] == 'Pending'
    
    # Admin approves
    success, msg = database.update_leave_status(req['id'], 'Approved', admin['id'], admin['username'])
    assert success is True
    
    # Verify leave request is approved
    updated_req = database.get_user_leave_requests(alice['id'])[0]
    assert updated_req['status'] == 'Approved'
    assert updated_req['reviewed_by'] == admin['id']
    
    # Verify balance was updated (15 days - 3 days = 12 days)
    updated_alice = database.get_user_by_username("alice")
    assert updated_alice['casual_balance'] == 12
    
    # Verify audit logs captured action
    logs = database.get_audit_logs()
    assert len(logs) == 1
    assert logs[0]['admin_id'] == admin['id']
    assert logs[0]['action'] == 'Leave Approved'
    assert f"Balance updated from 15 to 12" in logs[0]['details']

def test_insufficient_balance_rejection():
    """
    Verifies that system blocks approval if requested days exceed employee balance.
    """
    alice = database.get_user_by_username("alice")
    admin = database.get_user_by_username("admin")
    
    # Alice requests 30 days of Paid leave (but only has 20)
    database.apply_leave(
        user_id=alice['id'],
        leave_type='Paid',
        start_date='2026-07-01',
        end_date='2026-07-30',
        reason='Long vacation',
        ai_recommendation='Reject',
        ai_reason='Exceeds balance'
    )
    
    requests = database.get_user_leave_requests(alice['id'])
    req = requests[0]
    
    # Attempt approval
    success, msg = database.update_leave_status(req['id'], 'Approved', admin['id'], admin['username'])
    assert success is False
    assert "Insufficient Paid leave balance" in msg
    
    # Verify status is still pending and balance remains unchanged
    updated_req = database.get_user_leave_requests(alice['id'])[0]
    assert updated_req['status'] == 'Pending'
    
    updated_alice = database.get_user_by_username("alice")
    assert updated_alice['paid_balance'] == 20

def test_password_change_flow():
    """
    Verifies profile settings password update rules.
    """
    alice = database.get_user_by_username("alice")
    
    # Try with incorrect current password
    success, msg = auth.change_user_password(alice['id'], "wrongpassword", "newpassword123")
    assert success is False
    assert "Incorrect current password" in msg
    
    # Try with short password
    success, msg = auth.change_user_password(alice['id'], "password123", "short")
    assert success is False
    assert "at least 6 characters" in msg
    
    # Successful change
    success, msg = auth.change_user_password(alice['id'], "password123", "newpassword123")
    assert success is True
    assert "updated successfully" in msg
    
    # Verify new credentials work
    user_new = auth.authenticate_user("alice", "newpassword123")
    assert user_new is not None
    
    # Verify old credentials fail
    user_old = auth.authenticate_user("alice", "password123")
    assert user_old is None

def test_ai_agent_heuristics():
    """
    Tests local heuristic AI agent decision quality.
    """
    # Case 1: Over-limit balance rejection
    rec, reason = ai_agent.rule_based_analysis("Alice", "Casual", 20, "Holiday", 15)
    assert rec == 'Reject'
    assert "exceeds" in reason.lower()
    
    # Case 2: Zero or Negative duration
    rec, reason = ai_agent.rule_based_analysis("Alice", "Casual", 0, "No days", 15)
    assert rec == 'Reject'
    assert "invalid" in reason.lower()
    
    # Case 3: Medical Emergency (Sick leave)
    rec, reason = ai_agent.rule_based_analysis("Alice", "Sick", 2, "Going to hospital for surgery", 10)
    assert rec == 'Approve'
    assert "medical" in reason.lower() or "health" in reason.lower()
    
    # Case 4: Long Leave block escalation
    rec, reason = ai_agent.rule_based_analysis("Alice", "Paid", 12, "Tour of Europe", 20)
    assert rec == 'Escalate'
    assert "large leave block" in reason.lower() or "duration" in reason.lower()
    
    # Case 5: Vague reason escalation
    rec, reason = ai_agent.rule_based_analysis("Alice", "Casual", 3, "stuff", 10)
    assert rec == 'Escalate'
    assert "vague" in reason.lower() or "brief" in reason.lower()
    
    # Case 6: Red flag/Informal text escalation
    rec, reason = ai_agent.rule_based_analysis("Alice", "Casual", 1, "recovery from a wild party last night", 10)
    assert rec == 'Escalate'
    assert "informal" in reason.lower() or "non-standard" in reason.lower() or "party" in reason.lower()
    
    # Case 7: Legitimate Short Request approval
    rec, reason = ai_agent.rule_based_analysis("Alice", "Casual", 2, "Sister's wedding ceremony", 15)
    assert rec == 'Approve'
    assert "wedding" in reason.lower() or "priority" in reason.lower()
