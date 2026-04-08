"""Creator profile routes."""
import logging
import threading
from fastapi import APIRouter, Depends, HTTPException
from models.creator import CreatorProfileRequest, CreatorProfileResponse
from core.dependencies import get_db_conn, require_creator, get_current_user
from core.database import get_creator_profile
from core.config import GEMINI_API_KEY, DATABASE_PATH
from services.profile_service import save_creator_profile, run_ai_analysis, run_embedding_generation

logger = logging.getLogger("admatch")
router = APIRouter()


def _trigger_ai_background(user_id: str):
    """Run AI analysis + embedding in background thread."""
    try:
        from model_router import ModelRouter
        from core.database import get_db
        mr = ModelRouter(GEMINI_API_KEY)
        with get_db(DATABASE_PATH) as conn:
            run_ai_analysis(conn, user_id, "creator", mr)
            run_embedding_generation(conn, user_id, "creator", mr)
        logger.info(f"AI analysis complete for creator {user_id}")
    except Exception as e:
        from core.error_tracker import track_error
        track_error("ai_analysis_creator", e, {"user_id": user_id})


@router.put("/profile", response_model=CreatorProfileResponse)
def upsert_profile(data: CreatorProfileRequest, user: dict = Depends(require_creator), conn=Depends(get_db_conn)):
    result = save_creator_profile(conn, user["id"], data.model_dump())
    if GEMINI_API_KEY:
        threading.Thread(target=_trigger_ai_background, args=(user["id"],), daemon=True).start()
    return _to_response(result)


@router.get("/profile", response_model=CreatorProfileResponse)
def get_profile(user: dict = Depends(require_creator), conn=Depends(get_db_conn)):
    result = get_creator_profile(conn, user["id"])
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(result)


@router.get("/ai-status")
def ai_status(user: dict = Depends(require_creator), conn=Depends(get_db_conn)):
    profile = get_creator_profile(conn, user["id"])
    if not profile:
        return {"analyzed": False, "has_embedding": False}
    return {
        "analyzed": bool(profile.get("ai_profile_json")),
        "has_embedding": bool(profile.get("embedding_description")),
        "embedding_description": profile.get("embedding_description", ""),
    }


@router.get("/{user_id}", response_model=CreatorProfileResponse)
def get_creator(user_id: str, _user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    result = get_creator_profile(conn, user_id)
    if not result:
        raise HTTPException(status_code=404, detail="Creator not found")
    return _to_response(result)


def _to_response(d: dict) -> CreatorProfileResponse:
    return CreatorProfileResponse(
        user_id=d.get("user_id", d.get("id", "")),
        display_name=d.get("display_name", ""),
        niche=d.get("niche", ""),
        description=d.get("description", ""),
        follower_count=d.get("follower_count", 0),
        engagement_rate=d.get("engagement_rate", 0.0),
        content_style=d.get("content_style", []),
        min_fee=d.get("min_fee", 0),
        max_fee=d.get("max_fee", 0),
        values=d.get("values", []),
        audience_description=d.get("audience_description", ""),
        audience_acceptance_threshold=d.get("audience_acceptance_threshold", 0.35),
        ai_profile_json=d.get("ai_profile_json"),
        embedding_description=d.get("embedding_description"),
    )
