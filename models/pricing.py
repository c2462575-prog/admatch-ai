"""Pricing-related Pydantic models."""
from pydantic import BaseModel


class PriceEstimateRequest(BaseModel):
    followers: int
    engagement_rate: float
    category: str = "lifestyle"


class PriceEstimateResponse(BaseModel):
    base_price: float
    suggested_range: tuple[float, float]


class RoiEstimateRequest(BaseModel):
    price: float
    expected_reach: int
    conversion_rate: float


class RoiEstimateResponse(BaseModel):
    estimated_conversions: float
    cost_per_conversion: float
    roi_score: float
