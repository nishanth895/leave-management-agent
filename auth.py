import bcrypt
import database

def hash_password(password: str) -> str:
    """
    Hashes a password string using bcrypt.
    """
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verifies a plain text password against a hashed bcrypt password.
    """
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False

def authenticate_user(identifier, password):
    """
    Authenticates a user by username or email against database credentials.

    Email login smart rule:
      If the identifier is an email (contains '@'), the user may also log in
      using just the part before '@' as the password.
      Example: email=nishanth@gmail.com  →  password accepted: 'nishanth'
      (The system first tries the stored hash; if that fails it checks the
       email-prefix shortcut and re-hashes + stores it on first match.)
    """
    # Determine whether identifier looks like an email
    if isinstance(identifier, str) and '@' in identifier:
        user = database.get_user_by_email(identifier)
    else:
        user = database.get_user_by_username(identifier)

    if not user:
        return None

    # 1. Standard bcrypt check (works for all users)
    if verify_password(password, user['password_hash']):
        return user

    # 2. Email-prefix shortcut: if logged in with email, allow prefix as password
    if isinstance(identifier, str) and '@' in identifier:
        email_prefix = identifier.split('@')[0]  # e.g. 'nishanth' from 'nishanth@gmail.com'
        if password == email_prefix:
            # Re-hash and save the new password so future logins use bcrypt
            new_hash = hash_password(email_prefix)
            database.update_user_password(user['id'], new_hash)
            # Return fresh user row
            return database.get_user_by_id(user['id'])

    return None

def change_user_password(user_id, current_password, new_password):
    """
    Verifies current password and updates to new password.
    Returns tuple (success: bool, message: str)
    """
    user = database.get_user_by_id(user_id)
    if not user:
        return False, "User not found."
        
    if not verify_password(current_password, user['password_hash']):
        return False, "Incorrect current password."
        
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."
        
    hashed_new = hash_password(new_password)
    database.update_user_password(user_id, hashed_new)
    return True, "Password updated successfully."
