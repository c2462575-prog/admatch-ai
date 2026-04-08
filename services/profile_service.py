"""Profile service: wraps existing AI agents for profile analysis."""
import json
import pickle
from core.database import (
    upsert_advertiser_profile, get_advertiser_profile,
    upsert_creator_profile, get_creator_profile,
    update_advertiser_embedding, update_creator_embedding,
)


def save_advertiser_profile(conn, user_id: str, data: dict) -> dict:
    """Save advertiser profile to DB."""
    return upsert_advertiser_profile(conn, user_id, data)


def save_creator_profile(conn, user_id: str, data: dict) -> dict:
    """Save creator profile to DB."""
    return upsert_creator_profile(conn, user_id, data)


def profile_to_agent_dict(profile: dict, role: str) -> dict:
    """Convert DB profile dict to the format existing agents expect (matching data/scenarios.py schema)."""
    if role == "advertiser":
        return {
            "id": profile.get("user_id", profile.get("id", "")),
            "name": profile.get("display_name", ""),
            "name_cn": profile.get("display_name", ""),
            "industry": profile.get("industry", ""),
            "description": profile.get("description", ""),
            "budget_range": profile.get("budget_range", "medium"),
            "budget_value": profile.get("budget_value", 0),
            "target_audience": profile.get("target_audience", ""),
            "values": profile.get("values", []),
            "campaign_goal": profile.get("campaign_goal", ""),
        }
    else:
        return {
            "id": profile.get("user_id", profile.get("id", "")),
            "name": profile.get("display_name", ""),
            "name_cn": profile.get("display_name", ""),
            "niche": profile.get("niche", ""),
            "description": profile.get("description", ""),
            "follower_count": profile.get("follower_count", 0),
            "engagement_rate": profile.get("engagement_rate", 0.0),
            "content_style": profile.get("content_style", []),
            "min_fee": profile.get("min_fee", 0),
            "max_fee": profile.get("max_fee", 0),
            "values": profile.get("values", []),
        }


def profile_to_audience_dict(creator_profile: dict) -> dict:
    """Convert creator profile to audience dict matching data/scenarios.py schema."""
    uid = creator_profile.get("user_id", creator_profile.get("id", ""))
    return {
        "id": f"{uid}_audience",
        "creator_id": uid,
        "name": f"{creator_profile.get('display_name', '')} 的粉絲群體",
        "description": creator_profile.get("audience_description", ""),
        "acceptance_threshold": creator_profile.get("audience_acceptance_threshold", 0.35),
        "sensitivity_factors": creator_profile.get("audience_sensitivity_factors", []),
        "rejection_triggers": creator_profile.get("audience_rejection_triggers", []),
    }


def run_ai_analysis(conn, user_id: str, role: str, router):
    """Run AI agent analysis on a profile. Requires Gemini API."""
    if role == "advertiser":
        profile = get_advertiser_profile(conn, user_id)
        if not profile:
            return None
        agent_dict = profile_to_agent_dict(profile, "advertiser")
        from agents.advertiser_agent import AdvertiserAgent
        agent = AdvertiserAgent(agent_dict, router)
        result = agent.analyze_profile()
        if result:
            conn.execute(
                "UPDATE advertiser_profiles SET ai_profile_json=? WHERE user_id=?",
                (json.dumps(result, ensure_ascii=False), user_id),
            )
        return result
    else:
        profile = get_creator_profile(conn, user_id)
        if not profile:
            return None
        agent_dict = profile_to_agent_dict(profile, "creator")
        from agents.creator_agent import CreatorAgent
        agent = CreatorAgent(agent_dict, router)
        result = agent.analyze_profile()
        if result:
            conn.execute(
                "UPDATE creator_profiles SET ai_profile_json=? WHERE user_id=?",
                (json.dumps(result, ensure_ascii=False), user_id),
            )
        return result


def run_embedding_generation(conn, user_id: str, role: str, router):
    """Generate embedding for a profile using existing EmbeddingEngine."""
    from engine.embedding import EmbeddingEngine
    engine = EmbeddingEngine(router)

    if role == "advertiser":
        profile = get_advertiser_profile(conn, user_id)
        if not profile:
            return None
        agent_dict = profile_to_agent_dict(profile, "advertiser")
        desc = engine.generate_embedding_description("advertiser", agent_dict)
        vector = engine.generate_embedding_vector(desc)
        if desc and vector:
            update_advertiser_embedding(conn, user_id, desc, pickle.dumps(vector))
        return {"description": desc, "vector_dim": len(vector) if vector else 0}
    else:
        profile = get_creator_profile(conn, user_id)
        if not profile:
            return None
        agent_dict = profile_to_agent_dict(profile, "creator")
        desc = engine.generate_embedding_description("creator", agent_dict)
        vector = engine.generate_embedding_vector(desc)
        if desc and vector:
            update_creator_embedding(conn, user_id, desc, pickle.dumps(vector))
        return {"description": desc, "vector_dim": len(vector) if vector else 0}
