"""Negotiation-related Pydantic models."""
from pydantic import BaseModel
from typing import Optional


class NegotiationRoundResponse(BaseModel):
    round_num: int
    advertiser_message: str = ""
    creator_message: str = ""
    audience_score: Optional[float] = None
    audience_feedback: Optional[str] = None
    intervention_warning: Optional[str] = None


class NegotiationResponse(BaseModel):
    id: str
    match_id: str
    advertiser_id: str
    creator_id: str
    status: str = "in_progress"
    current_round: int = 0
    final_price: int = 0
    summary: Optional[str] = None
    rounds: list[NegotiationRoundResponse] = []
    advertiser_name: str = ""
    creator_name: str = ""


class NegotiationStartRequest(BaseModel):
    match_id: str
