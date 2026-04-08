"""Advertiser profile routes."""
import os
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException
from models.advertiser import AdvertiserProfileRequest, AdvertiserProfileResponse
from core.dependencies import get_db_conn, require_advertiser, get_current_user
from core.database import get_advertiser_profile
from core.config import GEMINI_API_KEY, DATABASE_PATH
from services.profile_service import save_advertiser_profile, run_ai_analysis, run_embedding_generation

logger = logging.getLogger("admatch")
router = APIRouter()


def _trigger_ai_background(user_id: str):
    """Run AI analysis + embedding in background thread."""
    try:
        from model_router import ModelRouter
        from core.database import get_db
        mr = ModelRouter(GEMINI_API_KEY)
        with get_db(DATABASE_PATH) as conn:
            run_ai_analysis(conn, user_id, "advertiser", mr)
            run_embedding_generation(conn, user_id, "advertiser", mr)
        logger.info(f"AI analysis complete for advertiser {user_id}")
    except Exception as e:
        logger.warning(f"AI analysis failed for advertiser {user_id}: {e}")


@router.put("/profile", response_model=AdvertiserProfileResponse)
def upsert_profile(data: AdvertiserProfileRequest, user: dict = Depends(require_advertiser), conn=Depends(get_db_conn)):
    result = save_advertiser_profile(conn, user["id"], data.model_dump())
    if GEMINI_API_KEY:
        threading.Thread(target=_trigger_ai_background, args=(user["id"],), daemon=True).start()
    return _to_response(result)


@router.get("/profile", response_model=AdvertiserProfileResponse)
def get_profile(user: dict = Depends(require_advertiser), conn=Depends(get_db_conn)):
    result = get_advertiser_profile(conn, user["id"])
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(result)


@router.get("/ai-status")
def ai_status(user: dict = Depends(require_advertiser), conn=Depends(get_db_conn)):
    profile = get_advertiser_profile(conn, user["id"])
    if not profile:
        return {"analyzed": False, "has_embedding": False}
    return {
        "analyzed": bool(profile.get("ai_profile_json")),
        "has_embedding": bool(profile.get("embedding_description")),
        "embedding_description": profile.get("embedding_description", ""),
    }


@router.get("/{user_id}", response_model=AdvertiserProfileResponse)
def get_advertiser(user_id: str, _user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    result = get_advertiser_profile(conn, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    return _to_response(result)


def _to_response(d: dict) -> AdvertiserProfileResponse:
    return AdvertiserProfileResponse(
        user_id=d.get("user_id", d.get("id", "")),
        display_name=d.get("display_name", ""),
        industry=d.get("industry", ""),
        description=d.get("description", ""),
        budget_range=d.get("budget_range", "medium"),
        budget_value=d.get("budget_value", 0),
        target_audience=d.get("target_audience", ""),
        values=d.get("values", []),
        campaign_goal=d.get("campaign_goal", ""),
        ai_profile_json=d.get("ai_profile_json"),
        embedding_description=d.get("embedding_description"),
    )
