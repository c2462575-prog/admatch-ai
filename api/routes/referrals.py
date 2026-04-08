"""Referral system routes."""
from fastapi import APIRouter, Depends
from core.dependencies import get_db_conn, get_current_user
from core.database import create_referral_code, get_referral_stats

router = APIRouter()


@router.get("/my-code")
def get_my_referral_code(user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    code = create_referral_code(conn, user["id"])
    stats = get_referral_stats(conn, user["id"])
    return {"code": code, **stats}


@router.get("/stats")
def get_my_referral_stats(user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    return get_referral_stats(conn, user["id"])
