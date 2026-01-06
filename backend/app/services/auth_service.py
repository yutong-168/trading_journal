from werkzeug.security import generate_password_hash, check_password_hash

from app.repos.user_repo import get_user_by_email, create_user

def register_user(email: str, password: str):
    existing_user = get_user_by_email(email)
    if existing_user is not None:
        raise ValueError("User already exists")
    
    password_hash = generate_password_hash(password)
    
    create_user(email, password_hash)
    
    return True

def login_user(email: str, password: str):
    user = get_user_by_email(email)
    if user is None:
        raise ValueError("User not found")
    
    user_id, user_email, password_hash, created_at = user
    
    if not check_password_hash(password_hash, password):
        raise ValueError("Invalid password")
    
    return {
        "user_id": user_id,
        "email": user_email
    }