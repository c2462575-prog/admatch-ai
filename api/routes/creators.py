"""Creator profile routes."""
from fastapi import APIRouter, Depends, HTTPException
from models.creator import CreatorProfileRequest, CreatorProfileResponse
from core.dependencies import get_db_conn, require_creator, get_current_user
from core.database import get_creator_profile
from services.profile_service import save_creator_profile

router = APIRouter()


@router.put("/profile", response_model=CreatorProfileResponse)
def upsert_profile(data: CreatorProfileRequest, user: dict = Depends(require_creator), conn=Depends(get_db_conn)):
    result = save_creator_profile(conn, user["id"], data.model_dump())
    return _to_response(result)


@router.get("/profile", response_model=CreatorProfileResponse)
def get_profile(user: dict = Depends(require_creator), conn=Depends(get_db_conn)):
    result = get_creator_profile(conn, user["id"])
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(result)


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
