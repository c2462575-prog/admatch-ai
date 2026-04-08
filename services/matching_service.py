"""Matching service: wraps existing matching engine for web API."""
import pickle
from core.database import (
    get_advertiser_profile, get_all_creator_profiles,
    get_creator_profile, get_all_advertiser_profiles,
    create_match, get_matches_for_user,
    increment_match_usage, check_match_limit,
)
from core.config import FREE_MATCHES_PER_MONTH
from engine.matching import MatchingEngine
from services.profile_service import profile_to_agent_dict, profile_to_audience_dict
from fastapi import HTTPException


def run_matching_for_user(conn, user_id: str, role: str) -> list[dict]:
    """Run matching algorithm for a user against all candidates of opposite role."""
    if not check_match_limit(conn, user_id, FREE_MATCHES_PER_MONTH):
        raise HTTPException(status_code=429, detail="Monthly match limit reached. Upgrade to continue.")

    engine = MatchingEngine()

    if role == "advertiser":
        profile = get_advertiser_profile(conn, user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Advertiser profile not found. Please complete your profile first.")
        candidates = get_all_creator_profiles(conn)
        if not candidates:
            return []

        adv_dict = profile_to_agent_dict(profile, "advertiser")
        adv_vector = pickle.loads(profile["embedding_vector"]) if profile.get("embedding_vector") else None

        results = []
        for cand in candidates:
            creator_dict = profile_to_agent_dict(cand, "creator")
            audience_dict = profile_to_audience_dict(cand)
            cand_vector = pickle.loads(cand["embedding_vector"]) if cand.get("embedding_vector") else None

            if adv_vector and cand_vector:
                score = engine.calculate_match(adv_dict, creator_dict, adv_vector, cand_vector, audience_dict)
                scores = {
                    "embedding_score": score.embedding_score,
                    "audience_score": score.audience_score,
                    "budget_score": score.budget_score,
                    "values_score": score.values_score,
                    "weighted_score": score.weighted_score,
                }
            else:
                # Fallback: compute without embeddings
                scores = _compute_partial_scores(engine, adv_dict, creator_dict, audience_dict)

            match = create_match(conn, user_id, cand["user_id"], scores)
            match["partner_name"] = cand.get("display_name", "")
            results.append(match)

    else:  # creator
        profile = get_creator_profile(conn, user_id)
        if not profile:
            raise HTTPException(status_code=404, detail="Creator profile not found. Please complete your profile first.")
        candidates = get_all_advertiser_profiles(conn)
        if not candidates:
            return []

        creator_dict = profile_to_agent_dict(profile, "creator")
        audience_dict = profile_to_audience_dict(profile)
        creator_vector = pickle.loads(profile["embedding_vector"]) if profile.get("embedding_vector") else None

        results = []
        for cand in candidates:
            adv_dict = profile_to_agent_dict(cand, "advertiser")
            cand_vector = pickle.loads(cand["embedding_vector"]) if cand.get("embedding_vector") else None

            if creator_vector and cand_vector:
                score = engine.calculate_match(adv_dict, creator_dict, cand_vector, creator_vector, audience_dict)
                scores = {
                    "embedding_score": score.embedding_score,
                    "audience_score": score.audience_score,
                    "budget_score": score.budget_score,
                    "values_score": score.values_score,
                    "weighted_score": score.weighted_score,
                }
            else:
                scores = _compute_partial_scores(engine, adv_dict, creator_dict, audience_dict)

            match = create_match(conn, cand["user_id"], user_id, scores)
            match["partner_name"] = cand.get("display_name", "")
            results.append(match)

    increment_match_usage(conn, user_id)
    results.sort(key=lambda x: x.get("weighted_score", 0), reverse=True)
    return results


def _compute_partial_scores(engine, adv_dict, creator_dict, audience_dict) -> dict:
    """Compute scores when embedding vectors are not available.
    Uses keyword overlap as embedding_score fallback instead of 0."""
    audience_score = engine.calculate_audience_fit(adv_dict, creator_dict)
    budget_score = engine.calculate_budget_fit(adv_dict, creator_dict)
    values_score = engine.calculate_values_alignment(adv_dict, creator_dict)
    embedding_score = _keyword_similarity(adv_dict, creator_dict)
    weighted = (0.40 * embedding_score + 0.25 * audience_score
                + 0.20 * budget_score + 0.15 * values_score)
    return {
        "embedding_score": round(embedding_score, 4),
        "audience_score": audience_score,
        "budget_score": budget_score,
        "values_score": values_score,
        "weighted_score": round(weighted, 4),
    }


def _keyword_similarity(adv_dict: dict, creator_dict: dict) -> float:
    """Fallback embedding score using keyword overlap from descriptions and tags."""
    adv_words = set()
    for field in ("description", "industry", "target_audience", "campaign_goal"):
        text = str(adv_dict.get(field, "")).lower()
        adv_words.update(w for w in text.split() if len(w) > 2)
    for v in adv_dict.get("values", []):
        adv_words.add(v.lower())

    creator_words = set()
    for field in ("description", "niche"):
        text = str(creator_dict.get(field, "")).lower()
        creator_words.update(w for w in text.split() if len(w) > 2)
    for tag in creator_dict.get("content_style", []):
        creator_words.add(tag.lower())
    for v in creator_dict.get("values", []):
        creator_words.add(v.lower())

    if not adv_words or not creator_words:
        return 0.3  # neutral default
    overlap = len(adv_words & creator_words)
    union = len(adv_words | creator_words)
    return overlap / union if union > 0 else 0.3
