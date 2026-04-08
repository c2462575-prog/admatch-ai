"""Creator profile Pydantic models."""
from pydantic import BaseModel, Field
from typing import Optional


class CreatorProfileRequest(BaseModel):
    niche: str = ""
    description: str = ""
    follower_count: int = 0
    engagement_rate: float = 0.0
    content_style: list[str] = []
    min_fee: int = 0
    max_fee: int = 0
    values: list[str] = []
    audience_description: str = ""
    audience_acceptance_threshold: float = 0.35
    audience_sensitivity_factors: list[str] = []
    audience_rejection_triggers: list[str] = []


class CreatorProfileResponse(BaseModel):
    user_id: str
    display_name: str = ""
    niche: str = ""
    description: str = ""
    follower_count: int = 0
    engagement_rate: float = 0.0
    content_style: list[str] = []
    min_fee: int = 0
    max_fee: int = 0
    values: list[str] = []
    audience_description: str = ""
    audience_acceptance_threshold: float = 0.35
    ai_profile_json: Optional[str] = None
    embedding_description: Optional[str] = None
