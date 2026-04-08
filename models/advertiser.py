"""Advertiser profile Pydantic models."""
from pydantic import BaseModel, Field
from typing import Optional


class AdvertiserProfileRequest(BaseModel):
    industry: str = ""
    description: str = ""
    budget_range: str = "medium"
    budget_value: int = 0
    target_audience: str = ""
    values: list[str] = []
    campaign_goal: str = ""


class AdvertiserProfileResponse(BaseModel):
    user_id: str
    display_name: str = ""
    industry: str = ""
    description: str = ""
    budget_range: str = "medium"
    budget_value: int = 0
    target_audience: str = ""
    values: list[str] = []
    campaign_goal: str = ""
    ai_profile_json: Optional[str] = None
    embedding_description: Optional[str] = None
