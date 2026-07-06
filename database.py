import sqlite3
import datetime
import bcrypt
import os

# On Streamlit Cloud, use /tmp for writable SQLite storage
# Locally, use the current directory
if os.path.exists("/tmp"):
    DB_NAME = "/tmp/leave_management.db"
else:
    DB_NAME = "leave_management.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Create Users Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('admin', 'employee')),
        name TEXT NOT NULL,
        casual_balance INTEGER DEFAULT 15,
        sick_balance INTEGER DEFAULT 10,
        paid_balance INTEGER DEFAULT 20
    )
    """)
    
    # 2. Create Leave Requests Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        leave_type TEXT NOT NULL CHECK(leave_type IN ('Casual', 'Sick', 'Paid')),
        start_date TEXT NOT NULL,
        end_date TEXT NOT NULL,
        reason TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Pending' CHECK(status IN ('Pending', 'Approved', 'Rejected')),
        ai_recommendation TEXT NOT NULL CHECK(ai_recommendation IN ('Approve', 'Escalate', 'Reject')),
        ai_reason TEXT,
        submitted_at TEXT NOT NULL,
        reviewed_by INTEGER,
        reviewed_at TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (reviewed_by) REFERENCES users(id)
    )
    """)
    
    # 3. Create Audit Logs Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS audit_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        target_request_id INTEGER,
        details TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        FOREIGN KEY (admin_id) REFERENCES users(id),
        FOREIGN KEY (target_request_id) REFERENCES leave_requests(id)
    )
    """)
    
    conn.commit()
    
    # Ensure email column exists for older DBs (safe add)
    cursor.execute("PRAGMA table_info(users)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if 'email' not in existing_columns:
        cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_users_email ON users(email)")
        conn.commit()
        cursor.execute("UPDATE users SET email = LOWER(username) || '@example.com' WHERE email IS NULL OR email = ''")
        conn.commit()
    
    # Seed default users if users table is empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        # Password = email prefix (part before @)
        # e.g. admin@example.com → password: admin
        users_to_seed = [
            ("admin", "admin@example.com", "admin123",    "admin",    "System Administrator", 15, 10, 20),
            ("alice", "alice@example.com", "password123", "employee", "Alice Smith",           15, 10, 20),
            ("bob",   "bob@example.com",   "password123", "employee", "Bob Jones",             15, 10, 20),
        ]

        for username, email, password, role, name, casual, sick, paid in users_to_seed:
            try:
                salt = bcrypt.gensalt(rounds=12)
                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
                cursor.execute("""
                INSERT OR IGNORE INTO users (username, email, password_hash, role, name, casual_balance, sick_balance, paid_balance)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (username, email, hashed_pw, role, name, casual, sick, paid))
            except Exception as e:
                # Skip if user already exists
                continue

        conn.commit()

    conn.close()

def get_user_by_username(username):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (username,)).fetchone()
    conn.close()
    return user


def get_user_by_email(email):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email,)).fetchone()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    return user

def update_user_password(user_id, hashed_password):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (hashed_password, user_id))
    conn.commit()
    conn.close()

def register_user(name, email, password, role='employee'):
    """
    Registers a new user. Username is derived from email prefix.
    Returns (success: bool, message: str)
    """
    import bcrypt as _bcrypt
    username = email.split('@')[0].lower()

    # Check duplicates
    if get_user_by_email(email):
        return False, "This email is already registered."
    if get_user_by_username(username):
        return False, f"Username '{username}' is already taken. Please use a different email."

    try:
        salt = _bcrypt.gensalt(rounds=12)
        hashed = _bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        conn = get_db_connection()
        conn.execute("""
            INSERT INTO users (username, email, password_hash, role, name, casual_balance, sick_balance, paid_balance)
            VALUES (?, ?, ?, ?, ?, 15, 10, 20)
        """, (username, email.lower(), hashed, role, name))
        conn.commit()
        conn.close()
        return True, f"Account created! You can now sign in as '{email}'."
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def get_all_employees():
    conn = get_db_connection()
    employees = conn.execute("SELECT * FROM users WHERE role = 'employee'").fetchall()
    conn.close()
    return employees

def check_leave_overlap(user_id, start_date, end_date):
    """
    Checks if there are any existing active (Pending or Approved) leave requests
    for the user that overlap with the proposed start_date and end_date.
    Overlap condition: (start_date <= existing_end_date) AND (end_date >= existing_start_date)
    """
    conn = get_db_connection()
    overlapping = conn.execute("""
        SELECT * FROM leave_requests 
        WHERE user_id = ? 
          AND status IN ('Pending', 'Approved') 
          AND start_date <= ? 
          AND end_date >= ?
    """, (user_id, end_date, start_date)).fetchall()
    conn.close()
    return overlapping

def apply_leave(user_id, leave_type, start_date, end_date, reason, ai_recommendation, ai_reason):
    conn = get_db_connection()
    cursor = conn.cursor()
    submitted_at = datetime.datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO leave_requests (user_id, leave_type, start_date, end_date, reason, status, ai_recommendation, ai_reason, submitted_at)
        VALUES (?, ?, ?, ?, ?, 'Pending', ?, ?, ?)
    """, (user_id, leave_type, start_date, end_date, reason, ai_recommendation, ai_reason, submitted_at))
    conn.commit()
    conn.close()

def get_user_leave_requests(user_id):
    conn = get_db_connection()
    requests = conn.execute("""
        SELECT * FROM leave_requests 
        WHERE user_id = ? 
        ORDER BY submitted_at DESC
    """, (user_id,)).fetchall()
    conn.close()
    return requests

def get_all_leave_requests():
    conn = get_db_connection()
    requests = conn.execute("""
        SELECT lr.*, u.name as employee_name, u.username as employee_username, 
               u.casual_balance, u.sick_balance, u.paid_balance
        FROM leave_requests lr
        JOIN users u ON lr.user_id = u.id
        ORDER BY lr.submitted_at DESC
    """, []).fetchall()
    conn.close()
    return requests

def update_leave_status(request_id, status, admin_id, admin_username):
    """
    Updates leave status. If status is Approved, deducts leave days from balance.
    Logs action to audit_logs.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Fetch the leave request details first
        request = cursor.execute("""
            SELECT lr.*, u.casual_balance, u.sick_balance, u.paid_balance 
            FROM leave_requests lr
            JOIN users u ON lr.user_id = u.id
            WHERE lr.id = ?
        """, (request_id,)).fetchone()
        
        if not request:
            conn.close()
            return False, "Leave request not found."
            
        if request['status'] != 'Pending':
            conn.close()
            return False, f"Leave request already {request['status']}."
            
        start_date = datetime.datetime.strptime(request['start_date'], "%Y-%m-%d")
        end_date = datetime.datetime.strptime(request['end_date'], "%Y-%m-%d")
        leave_days = (end_date - start_date).days + 1
        
        # Determine balance field name
        leave_type = request['leave_type']
        balance_col = ""
        if leave_type == 'Casual':
            balance_col = 'casual_balance'
        elif leave_type == 'Sick':
            balance_col = 'sick_balance'
        elif leave_type == 'Paid':
            balance_col = 'paid_balance'
            
        current_balance = request[balance_col]
        
        if status == 'Approved':
            if current_balance < leave_days:
                conn.close()
                return False, f"Insufficient {leave_type} leave balance (Required: {leave_days}, Available: {current_balance})."
                
            # Deduct balance
            new_balance = current_balance - leave_days
            cursor.execute(f"UPDATE users SET {balance_col} = ? WHERE id = ?", (new_balance, request['user_id']))
            details = f"Approved {leave_days} day(s) of {leave_type} leave. Balance updated from {current_balance} to {new_balance}."
        else:
            details = f"Rejected {leave_days} day(s) of {leave_type} leave."
            
        # Update request status
        reviewed_at = datetime.datetime.now().isoformat()
        cursor.execute("""
            UPDATE leave_requests 
            SET status = ?, reviewed_by = ?, reviewed_at = ? 
            WHERE id = ?
        """, (status, admin_id, reviewed_at, request_id))
        
        # Log to audit_logs
        timestamp = datetime.datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO audit_logs (admin_id, action, target_request_id, details, timestamp)
            VALUES (?, ?, ?, ?, ?)
        """, (admin_id, f"Leave {status}", request_id, details, timestamp))
        
        conn.commit()
        conn.close()
        return True, "Success"
        
    except Exception as e:
        conn.rollback()
        conn.close()
        return False, str(e)

def log_audit(admin_id, action, target_request_id, details):
    conn = get_db_connection()
    cursor = conn.cursor()
    timestamp = datetime.datetime.now().isoformat()
    cursor.execute("""
        INSERT INTO audit_logs (admin_id, action, target_request_id, details, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (admin_id, action, target_request_id, details, timestamp))
    conn.commit()
    conn.close()

def get_audit_logs():
    conn = get_db_connection()
    logs = conn.execute("""
        SELECT al.*, u.username as admin_username, u.name as admin_name
        FROM audit_logs al
        JOIN users u ON al.admin_id = u.id
        ORDER BY al.timestamp DESC
    """).fetchall()
    conn.close()
    return logs
