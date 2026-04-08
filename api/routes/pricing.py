"""Pricing routes: public pricing calculator."""
from fastapi import APIRouter, HTTPException, Query
from models.pricing import PriceEstimateResponse, RoiEstimateResponse
from utils.price_calculator import calculate_creator_price, estimate_roi

router = APIRouter()


@router.get("/estimate", response_model=PriceEstimateResponse)
def price_estimate(followers: int = Query(10000, ge=1), engagement_rate: float = Query(0.05, gt=0), category: str = "lifestyle"):
    result = calculate_creator_price(followers, engagement_rate, category)
    return PriceEstimateResponse(**result)


@router.get("/roi", response_model=RoiEstimateResponse)
def roi_estimate(price: float = Query(5000, gt=0), expected_reach: int = Query(50000, ge=1), conversion_rate: float = Query(0.02, gt=0)):
    result = estimate_roi(price, expected_reach, conversion_rate)
    return RoiEstimateResponse(**result)
