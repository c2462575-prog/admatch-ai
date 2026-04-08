"""Matching-related Pydantic models."""
from pydantic import BaseModel
from typing import Optional


class MatchResultResponse(BaseModel):
    id: str
    advertiser_id: str
    creator_id: str
    partner_name: str = ""
    embedding_score: float = 0
    audience_score: float = 0
    budget_score: float = 0
    values_score: float = 0
    weighted_score: float = 0
    status: str = "pending"
    created_at: str = ""


class MatchDetailResponse(MatchResultResponse):
    advertiser_profile: Optional[dict] = None
    creator_profile: Optional[dict] = None
