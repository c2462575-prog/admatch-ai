"""Advertiser profile routes."""
from fastapi import APIRouter, Depends, HTTPException
from models.advertiser import AdvertiserProfileRequest, AdvertiserProfileResponse
from core.dependencies import get_db_conn, require_advertiser, get_current_user
from core.database import get_advertiser_profile
from services.profile_service import save_advertiser_profile

router = APIRouter()


@router.put("/profile", response_model=AdvertiserProfileResponse)
def upsert_profile(data: AdvertiserProfileRequest, user: dict = Depends(require_advertiser), conn=Depends(get_db_conn)):
    result = save_advertiser_profile(conn, user["id"], data.model_dump())
    return _to_response(result)


@router.get("/profile", response_model=AdvertiserProfileResponse)
def get_profile(user: dict = Depends(require_advertiser), conn=Depends(get_db_conn)):
    result = get_advertiser_profile(conn, user["id"])
    if not result:
        raise HTTPException(status_code=404, detail="Profile not found")
    return _to_response(result)


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
