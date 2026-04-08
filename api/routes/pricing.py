"""Pricing routes: public pricing calculator."""
from fastapi import APIRouter
from models.pricing import PriceEstimateResponse, RoiEstimateResponse
from utils.price_calculator import calculate_creator_price, estimate_roi

router = APIRouter()


@router.get("/estimate", response_model=PriceEstimateResponse)
def price_estimate(followers: int = 10000, engagement_rate: float = 0.05, category: str = "lifestyle"):
    result = calculate_creator_price(followers, engagement_rate, category)
    return PriceEstimateResponse(**result)


@router.get("/roi", response_model=RoiEstimateResponse)
def roi_estimate(price: float = 5000, expected_reach: int = 50000, conversion_rate: float = 0.02):
    result = estimate_roi(price, expected_reach, conversion_rate)
    return RoiEstimateResponse(**result)
