import streamlit as st
import datetime
import database
import ai_agent
import auth


def init_leave_form_state(session_state=None):
    """Initialize and preserve leave form values across reruns."""
    if session_state is None:
        session_state = {}

    defaults = {
        "leave_type": "Casual",
        "start_date": datetime.date.today(),
        "end_date": datetime.date.today(),
        "reason": "",
    }

    for key, value in defaults.items():
        if key not in session_state:
            session_state[key] = value

    return session_state


def reset_leave_form_state(session_state):
    """Clear the leave form values after a successful submission."""
    session_state["leave_type"] = "Casual"
    session_state["start_date"] = datetime.date.today()
    session_state["end_date"] = datetime.date.today()
    session_state["reason"] = ""


def show_employee_dashboard(user):
    # Fetch fresh user data to ensure up-to-date leave balances
    user_data = database.get_user_by_id(user['id'])

    # ── Global CSS for back button ──
    st.markdown("""
    <style>
    div[data-testid="column"]:first-child .stButton > button,
    button[kind="secondary"] {
        width: auto !important;
    }
    #back-btn-container button,
    .emp-back-btn > div > button,
    .emp-back-btn button {
        background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 14px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 18px rgba(37,99,235,0.25) !important;
        padding: 10px 22px !important;
        transition: all 0.22s ease !important;
        width: auto !important;
    }
    .emp-back-btn button:hover {
        transform: translateX(-3px) scale(1.03) !important;
        box-shadow: 0 8px 28px rgba(37,99,235,0.38) !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # ── Top bar row: Back | Title ──
    col_back, col_title = st.columns([1, 6])
    with col_back:
        st.markdown('<div class="emp-back-btn">', unsafe_allow_html=True)
        if st.button("← Back", key="emp_back_btn"):
            st.session_state.update({'page': 'home', 'logged_in': False, 'user': None, 'role': None})
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    with col_title:
        st.markdown(
            f"<h1 style='font-size:2.2rem; font-weight:800; color:#1e3a8a; margin:0; padding-top:6px;'>"
            f"Employee Portal &nbsp;"
            f"<span style='font-size:1.1rem; color:#2563eb; font-weight:500;'>Welcome back, {user_data['name']}! 👋</span>"
            f"</h1>",
            unsafe_allow_html=True
        )


    # Tabs for navigation within employee portal
    tab_apply, tab_history, tab_profile = st.tabs([
        "📊 Apply & Balance", 
        "📜 Leave History", 
        "👤 Profile Settings"
    ])
    
    # ---------------- TAB 1: APPLY & BALANCE ----------------
    form_state = init_leave_form_state(st.session_state)

    with tab_apply:
        st.markdown("### 📊 Your Leave Balances")
        
        # Display balance cards using Streamlit columns (no HTML)
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🏖️ Casual Leave",
                value=f"{user_data['casual_balance']} days",
                delta="Available"
            )
        
        with col2:
            st.metric(
                label="🏥 Sick Leave", 
                value=f"{user_data['sick_balance']} days",
                delta="Available"
            )
        
        with col3:
            st.metric(
                label="💰 Paid Leave",
                value=f"{user_data['paid_balance']} days",
                delta="Available"
            )
        
        st.markdown("---")
        st.markdown("### ✍️ Request New Leave")
        
        with st.form("leave_application_form", clear_on_submit=False):
            leave_type = st.selectbox(
                "Leave Type",
                ["Casual", "Sick", "Paid"],
                key="leave_type",
                index=["Casual", "Sick", "Paid"].index(form_state["leave_type"])
            )
            
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Start Date",
                    value=form_state["start_date"],
                    key="start_date",
                    min_value=datetime.date.today()
                )
            with col2:
                end_date = st.date_input(
                    "End Date",
                    value=form_state["end_date"],
                    key="end_date",
                    min_value=datetime.date.today()
                )
                
            reason = st.text_area(
                "Reason for Leave",
                value=form_state["reason"],
                key="reason",
                placeholder="Please describe why you need this leave request in detail..."
            )

            submit_btn = st.form_submit_button("Submit Leave Application")
            
            if submit_btn:
                # 1. Validation: Date checks
                if end_date < start_date:
                    st.error("❌ End Date cannot be earlier than Start Date.")
                # 2. Validation: Empty reason
                elif not reason.strip():
                    st.error("❌ Please provide a reason for your leave request.")
                else:
                    duration = (end_date - start_date).days + 1
                    
                    # 3. Validation: Balance checks
                    balance_col = ""
                    if leave_type == 'Casual':
                        balance_col = 'casual_balance'
                    elif leave_type == 'Sick':
                        balance_col = 'sick_balance'
                    elif leave_type == 'Paid':
                        balance_col = 'paid_balance'
                        
                    available_balance = user_data[balance_col]
                    
                    if duration > available_balance:
                        st.error(f"❌ Insufficient Balance. You requested {duration} days of {leave_type} leave, but only have {available_balance} days available.")
                    else:
                        # 4. Validation: Overlapping leaves check
                        overlaps = database.check_leave_overlap(user_data['id'], start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                        if overlaps:
                            st.error("⚠️ Overlapping Request Detected!")
                            for o in overlaps:
                                st.write(f"- Conflict: **{o['leave_type']} Leave** ({o['start_date']} to {o['end_date']}) - Status: **{o['status']}**")
                            st.info("Please adjust your dates and try again.")
                        else:
                            with st.spinner("AI evaluating leave request..."):
                                # Run AI evaluation (Gemini / Heuristics)
                                rec, rec_reason = ai_agent.analyze_leave_request(
                                    employee_name=user_data['name'],
                                    leave_type=leave_type,
                                    duration_days=duration,
                                    reason=reason,
                                    remaining_balance=available_balance
                                )
                                
                                # Insert leave request to database
                                database.apply_leave(
                                    user_id=user_data['id'],
                                    leave_type=leave_type,
                                    start_date=start_date.strftime("%Y-%m-%d"),
                                    end_date=end_date.strftime("%Y-%m-%d"),
                                    reason=reason,
                                    ai_recommendation=rec,
                                    ai_reason=rec_reason
                                )
                                
                            st.success(f"🎉 Leave application submitted successfully for {duration} day(s)!")
                            
                            # Visual AI response box
                            rec_color = "green" if rec == "Approve" else ("orange" if rec == "Escalate" else "red")
                            st.markdown(f"""
                            <div class="ai-box">
                                <h4 style="margin-top: 0; color: #1e3a8a;"><span class="ai-sparkle">✨</span> AI Agent Assessment</h4>
                                <p><strong>Preliminary Recommendation:</strong> <span style="color: {rec_color}; font-weight: bold;">{rec}</span></p>
                                <p><strong>AI Reasoning:</strong> <em>"{rec_reason}"</em></p>
                                <small style="color: #666;">Note: Final approval is pending Admin review.</small>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            reset_leave_form_state(st.session_state)

                            # Force re-render on next action to update balance instantly if needed (though it updates at approval, it's good practice)
                            st.rerun()

    # ---------------- TAB 2: LEAVE HISTORY ----------------
    with tab_history:
        st.subheader("Your Leave Application History")
        requests = database.get_user_leave_requests(user_data['id'])
        
        if not requests:
            st.info("You haven't submitted any leave requests yet.")
        else:
            # Custom HTML styling for history list
            for req in requests:
                status = req['status']
                badge_class = "status-pending" if status == 'Pending' else ("status-approved" if status == 'Approved' else "status-rejected")
                
                # Format Dates
                s_date = datetime.datetime.strptime(req['start_date'], "%Y-%m-%d").strftime("%b %d, %Y")
                e_date = datetime.datetime.strptime(req['end_date'], "%Y-%m-%d").strftime("%b %d, %Y")
                sub_date = datetime.datetime.fromisoformat(req['submitted_at']).strftime("%b %d, %Y %I:%M %p")
                
                duration = (datetime.datetime.strptime(req['end_date'], "%Y-%m-%d") - datetime.datetime.strptime(req['start_date'], "%Y-%m-%d")).days + 1
                
                st.markdown(f"""
                <div class="history-item">
                    <div class="history-header">
                        <span class="history-type">{req['leave_type']} Leave ({duration} Days)</span>
                        <span class="status-badge {badge_class}">{status}</span>
                    </div>
                    <div class="history-body">
                        <p><strong>Duration:</strong> {s_date} to {e_date}</p>
                        <p><strong>Reason:</strong> "{req['reason']}"</p>
                        <p><strong>Submitted On:</strong> {sub_date}</p>
                        {f"<p class='review-info'><strong>Reviewed:</strong> {req['reviewed_at'][:16].replace('T', ' ')}</p>" if req['reviewed_at'] else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ---------------- TAB 3: PROFILE SETTINGS ----------------
    with tab_profile:
        st.subheader("Account Profile Settings")
        
        st.markdown(f"""
        <div style="background-color: rgba(255, 255, 255, 0.05); padding: 15px; border-radius: 8px; margin-bottom: 20px;">
            <p><strong>Name:</strong> {user_data['name']}</p>
            <p><strong>Username:</strong> {user_data['username']}</p>
            <p><strong>Role:</strong> {user_data['role'].capitalize()}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("#### Change Password")
        with st.form("change_password_form"):
            current_password = st.text_input("Current Password", type="password")
            new_password = st.text_input("New Password", type="password", help="Must be at least 6 characters")
            confirm_password = st.text_input("Confirm New Password", type="password")
            
            update_btn = st.form_submit_button("Update Password")
            
            if update_btn:
                if new_password != confirm_password:
                    st.error("❌ New password and confirmation do not match.")
                elif len(new_password) < 6:
                    st.error("❌ New password must be at least 6 characters long.")
                else:
                    success, msg = auth.change_user_password(
                        user_id=user_data['id'],
                        current_password=current_password,
                        new_password=new_password
                    )
                    if success:
                        st.success(f"✅ {msg}")
                    else:
                        st.error(f"❌ {msg}")
