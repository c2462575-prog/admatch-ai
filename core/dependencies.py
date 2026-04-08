"""FastAPI dependency injection factories."""
from fastapi import Depends, HTTPException, Header
from core.database import get_db, get_user_by_id
from core.security import decode_jwt
from core.config import DATABASE_PATH


def get_db_conn():
    """Yield a database connection for request scope."""
    import sqlite3
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_current_user(authorization: str = Header(None), conn=Depends(get_db_conn)) -> dict:
    """Extract and validate JWT from Authorization header."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    token = authorization.split(" ", 1)[1]
    payload = decode_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = get_user_by_id(conn, payload.get("sub"))
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def require_advertiser(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "advertiser":
        raise HTTPException(status_code=403, detail="Advertiser role required")
    return user


def require_creator(user: dict = Depends(get_current_user)) -> dict:
    if user["role"] != "creator":
        raise HTTPException(status_code=403, detail="Creator role required")
    return user
