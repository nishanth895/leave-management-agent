import bcrypt
import sqlite3

DB = 'leave_management.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row

# New admin user details
username = "admin2005"
email    = "admin2005@gmail.com"
password = "admin2005"
role     = "admin"
name     = "Admin 2005"

# Check if already exists
existing = conn.execute("SELECT id FROM users WHERE email=? OR username=?", (email, username)).fetchone()
if existing:
    print(f"User already exists with id={existing['id']}")
else:
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode(), salt).decode()
    conn.execute("""
        INSERT INTO users (username, email, password_hash, role, name, casual_balance, sick_balance, paid_balance)
        VALUES (?, ?, ?, ?, ?, 15, 10, 20)
    """, (username, email, hashed, role, name))
    conn.commit()
    print(f"Created admin user:")
    print(f"  Email    : {email}")
    print(f"  Password : {password}")
    print(f"  Role     : {role}")

conn.close()
