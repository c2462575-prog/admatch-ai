"""Matching routes."""
from fastapi import APIRouter, Depends, HTTPException
from models.matching import MatchResultResponse, MatchDetailResponse
from core.dependencies import get_db_conn, get_current_user
from core.database import get_matches_for_user, get_match_by_id, get_advertiser_profile, get_creator_profile
from services.matching_service import run_matching_for_user

router = APIRouter()


@router.post("/run", response_model=list[MatchResultResponse])
def run_matching(user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    results = run_matching_for_user(conn, user["id"], user["role"])
    return [MatchResultResponse(**r) for r in results]


@router.get("/results", response_model=list[MatchResultResponse])
def get_results(limit: int = 20, user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    rows = get_matches_for_user(conn, user["id"], user["role"], limit)
    return [MatchResultResponse(**r) for r in rows]


@router.get("/results/{match_id}", response_model=MatchDetailResponse)
def get_match_detail(match_id: str, user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    match = get_match_by_id(conn, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match["advertiser_id"] != user["id"] and match["creator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    adv = get_advertiser_profile(conn, match["advertiser_id"])
    creator = get_creator_profile(conn, match["creator_id"])

    return MatchDetailResponse(
        **match,
        partner_name="",
        advertiser_profile=adv,
        creator_profile=creator,
    )
