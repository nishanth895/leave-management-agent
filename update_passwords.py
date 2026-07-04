import bcrypt
import sqlite3

DB = 'leave_management.db'
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
users = conn.execute('SELECT id, email FROM users').fetchall()

for u in users:
    email = u['email']
    prefix = email.split('@')[0]   # e.g. admin, alice, bob
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(prefix.encode(), salt).decode()
    conn.execute('UPDATE users SET password_hash=? WHERE id=?', (hashed, u['id']))
    print(f'Updated: email={email}  -->  password={prefix}')

conn.commit()
conn.close()
print('\nAll passwords updated successfully!')
