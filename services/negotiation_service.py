"""Negotiation service: per-round negotiation wrapping existing agents."""
import json
from fastapi import HTTPException
from core.database import (
    get_match_by_id, create_negotiation, get_negotiation,
    add_negotiation_round, complete_negotiation,
    get_advertiser_profile, get_creator_profile,
)
from services.profile_service import profile_to_agent_dict, profile_to_audience_dict


def start_negotiation(conn, match_id: str, user_id: str) -> dict:
    """Start a new negotiation for a match."""
    match = get_match_by_id(conn, match_id)
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")
    if match["advertiser_id"] != user_id and match["creator_id"] != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this match")

    neg = create_negotiation(conn, match_id, match["advertiser_id"], match["creator_id"])
    return neg


def run_next_round(conn, negotiation_id: str, router) -> dict:
    """Run the next negotiation round using AI agents."""
    neg = get_negotiation(conn, negotiation_id)
    if not neg:
        raise HTTPException(status_code=404, detail="Negotiation not found")
    if neg["status"] != "in_progress":
        raise HTTPException(status_code=400, detail="Negotiation already completed")

    next_round = neg["current_round"] + 1
    if next_round > 3:
        raise HTTPException(status_code=400, detail="All 3 rounds completed")

    # Load profiles
    adv_profile = get_advertiser_profile(conn, neg["advertiser_id"])
    creator_profile = get_creator_profile(conn, neg["creator_id"])
    if not adv_profile or not creator_profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    adv_dict = profile_to_agent_dict(adv_profile, "advertiser")
    creator_dict = profile_to_agent_dict(creator_profile, "creator")
    audience_dict = profile_to_audience_dict(creator_profile)

    # Get previous round context
    prev_rounds = neg.get("rounds", [])
    previous_response = ""
    if prev_rounds:
        last = prev_rounds[-1]
        previous_response = last.get("creator_message", "")

    # Import and run agents
    from agents.advertiser_agent import AdvertiserAgent
    from agents.creator_agent import CreatorAgent
    from agents.audience_agent import AudienceAgent

    adv_agent = AdvertiserAgent(adv_dict, router)
    creator_agent = CreatorAgent(creator_dict, router)
    audience_agent = AudienceAgent(audience_dict, router)

    # Generate offer and response
    adv_message = adv_agent.generate_offer(creator_dict, next_round, previous_response)
    adv_text = adv_message if isinstance(adv_message, str) else json.dumps(adv_message, ensure_ascii=False)

    creator_message = creator_agent.generate_response(adv_dict, next_round, adv_text)
    creator_text = creator_message if isinstance(creator_message, str) else json.dumps(creator_message, ensure_ascii=False)

    # Audience scoring
    audience_result = audience_agent.score_negotiation_round(adv_dict, next_round, adv_text, creator_text)
    audience_score = 0.5
    audience_feedback = ""
    intervention = None

    if isinstance(audience_result, dict):
        audience_score = audience_result.get("score", 0.5)
        audience_feedback = audience_result.get("feedback", "")
    elif isinstance(audience_result, (int, float)):
        audience_score = float(audience_result)

    # Check for intervention
    threshold = audience_dict.get("acceptance_threshold", 0.35)
    if audience_score < threshold:
        intervention_result = audience_agent.generate_intervention(audience_score, {
            "round": next_round,
            "advertiser_message": adv_text,
            "creator_message": creator_text,
        })
        intervention = intervention_result if isinstance(intervention_result, str) else json.dumps(intervention_result, ensure_ascii=False) if intervention_result else None

    round_data = {
        "advertiser_message": adv_text,
        "creator_message": creator_text,
        "audience_score": audience_score,
        "audience_feedback": audience_feedback,
        "intervention_warning": intervention,
    }
    add_negotiation_round(conn, negotiation_id, next_round, round_data)

    # If round 3, determine final outcome
    if next_round == 3:
        _determine_final_outcome(conn, negotiation_id, neg, adv_agent, creator_agent, audience_agent,
                                  adv_dict, creator_dict, audience_dict, audience_score, threshold)

    updated = get_negotiation(conn, negotiation_id)
    return updated


def _determine_final_outcome(conn, negotiation_id, neg, adv_agent, creator_agent, audience_agent,
                              adv_dict, creator_dict, audience_dict, final_audience_score, threshold):
    """After round 3, get final decisions from all parties."""
    # Audience verdict
    if final_audience_score < threshold:
        complete_negotiation(conn, negotiation_id, "audience_rejected", 0,
                           "Audience rejected the collaboration")
        return

    # Get agent final decisions
    try:
        adv_decision = adv_agent.decide_final_outcome(creator_dict)
        creator_decision = creator_agent.decide_final_outcome(adv_dict)

        adv_accepts = _parse_decision(adv_decision)
        creator_accepts = _parse_decision(creator_decision)

        if adv_accepts and creator_accepts:
            final_price = creator_dict.get("min_fee", 0)
            complete_negotiation(conn, negotiation_id, "success", final_price,
                               "Both parties agreed to collaborate")
        else:
            complete_negotiation(conn, negotiation_id, "failed", 0,
                               "One or both parties declined")
    except Exception:
        complete_negotiation(conn, negotiation_id, "failed", 0, "Error in final decision")


def _parse_decision(decision) -> bool:
    """Parse agent decision into boolean accept/reject."""
    if isinstance(decision, bool):
        return decision
    if isinstance(decision, dict):
        return decision.get("decision", "").lower() in ("accept", "yes", "agree")
    if isinstance(decision, str):
        return any(w in decision.lower() for w in ("accept", "agree", "yes", "deal"))
    return False
