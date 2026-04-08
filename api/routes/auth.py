"""Auth routes: register, login, me."""
from fastapi import APIRouter, Depends
from models.user import UserRegisterRequest, UserLoginRequest, TokenResponse, UserResponse
from services.auth_service import register, login
from core.dependencies import get_db_conn, get_current_user

router = APIRouter()


@router.post("/register", response_model=TokenResponse, status_code=201)
def register_user(data: UserRegisterRequest, conn=Depends(get_db_conn)):
    return register(conn, data.email, data.password, data.role, data.display_name, data.referral_code)


@router.post("/login", response_model=TokenResponse)
def login_user(data: UserLoginRequest, conn=Depends(get_db_conn)):
    return login(conn, data.email, data.password)


@router.get("/me", response_model=UserResponse)
def get_me(user: dict = Depends(get_current_user)):
    return UserResponse(
        id=user["id"],
        email=user["email"],
        role=user["role"],
        display_name=user["display_name"],
        plan=user.get("plan", "free"),
        matches_used_this_month=user.get("matches_used_this_month", 0),
    )
