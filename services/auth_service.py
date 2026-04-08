"""Authentication service: register, login."""
from fastapi import HTTPException
from core.security import hash_password, verify_password, create_jwt
from core.database import create_user, get_user_by_email, use_referral_code


def register(conn, email: str, password: str, role: str, display_name: str, referral_code: str = None) -> dict:
    existing = get_user_by_email(conn, email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    pw_hash = hash_password(password)
    user = create_user(conn, email, pw_hash, role, display_name)
    if referral_code:
        use_referral_code(conn, referral_code, user["id"])
    token = create_jwt({"sub": user["id"], "role": role})
    return {"access_token": token, "token_type": "bearer", "user": user}


def login(conn, email: str, password: str) -> dict:
    user = get_user_by_email(conn, email)
    if not user or not verify_password(password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_jwt({"sub": user["id"], "role": user["role"]})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "role": user["role"],
            "display_name": user["display_name"],
            "plan": user["plan"],
            "matches_used_this_month": user["matches_used_this_month"],
        },
    }
