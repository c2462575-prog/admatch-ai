"""Negotiation routes."""
import os
from fastapi import APIRouter, Depends, HTTPException
from models.negotiation import NegotiationResponse, NegotiationStartRequest
from core.dependencies import get_db_conn, get_current_user
from core.database import get_negotiation, get_negotiations_for_user
from services.negotiation_service import start_negotiation, run_next_round

router = APIRouter()


def _get_router():
    """Lazy-init ModelRouter (requires GEMINI_API_KEY)."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=503, detail="Gemini API key not configured")
    from model_router import ModelRouter
    return ModelRouter(api_key)


@router.post("/start", response_model=dict)
def start(data: NegotiationStartRequest, user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    return start_negotiation(conn, data.match_id, user["id"])


@router.post("/{negotiation_id}/next-round", response_model=dict)
def next_round(negotiation_id: str, user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    router = _get_router()
    return run_next_round(conn, negotiation_id, router)


@router.get("/{negotiation_id}", response_model=dict)
def get_neg(negotiation_id: str, user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    neg = get_negotiation(conn, negotiation_id)
    if not neg:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    if neg["advertiser_id"] != user["id"] and neg["creator_id"] != user["id"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    return neg


@router.get("/", response_model=list[dict])
def list_negotiations(user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    return get_negotiations_for_user(conn, user["id"])
