"""Test database CRUD operations."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database import (
    create_user, get_user_by_email, get_user_by_id,
    upsert_advertiser_profile, get_advertiser_profile,
    upsert_creator_profile, get_creator_profile,
    create_match, get_matches_for_user,
    create_negotiation, add_negotiation_round, get_negotiation,
    check_match_limit, increment_match_usage,
)
from core.security import hash_password


class TestUserCrud:
    def test_create_and_get(self, test_conn):
        user = create_user(test_conn, "test@x.com", hash_password("pw"), "advertiser", "Test")
        assert user["email"] == "test@x.com"
        found = get_user_by_email(test_conn, "test@x.com")
        assert found["display_name"] == "Test"
        found2 = get_user_by_id(test_conn, user["id"])
        assert found2["email"] == "test@x.com"

    def test_nonexistent_user(self, test_conn):
        assert get_user_by_email(test_conn, "nope@x.com") is None
        assert get_user_by_id(test_conn, "fake-id") is None


class TestAdvertiserProfile:
    def test_upsert_and_get(self, test_conn):
        user = create_user(test_conn, "adv@x.com", hash_password("pw"), "advertiser", "Brand")
        profile = upsert_advertiser_profile(test_conn, user["id"], {
            "industry": "tech", "description": "A brand", "budget_value": 100000, "values": ["innovation"],
        })
        assert profile["industry"] == "tech"
        fetched = get_advertiser_profile(test_conn, user["id"])
        assert fetched["budget_value"] == 100000
        assert "innovation" in fetched["values"]


class TestCreatorProfile:
    def test_upsert_and_get(self, test_conn):
        user = create_user(test_conn, "cre@x.com", hash_password("pw"), "creator", "Creator")
        profile = upsert_creator_profile(test_conn, user["id"], {
            "niche": "lifestyle", "follower_count": 50000, "engagement_rate": 0.05,
            "content_style": ["coffee", "travel"], "values": ["authenticity"],
        })
        assert profile["niche"] == "lifestyle"
        fetched = get_creator_profile(test_conn, user["id"])
        assert fetched["follower_count"] == 50000
        assert "coffee" in fetched["content_style"]


class TestMatching:
    def test_create_and_get_matches(self, test_conn):
        adv = create_user(test_conn, "a@x.com", hash_password("pw"), "advertiser", "A")
        cre = create_user(test_conn, "c@x.com", hash_password("pw"), "creator", "C")
        scores = {"embedding_score": 0.8, "audience_score": 0.7, "budget_score": 0.9, "values_score": 0.6, "weighted_score": 0.78}
        create_match(test_conn, adv["id"], cre["id"], scores)
        matches = get_matches_for_user(test_conn, adv["id"], "advertiser")
        assert len(matches) == 1
        assert matches[0]["weighted_score"] == 0.78


class TestNegotiation:
    def test_full_negotiation_flow(self, test_conn):
        adv = create_user(test_conn, "na@x.com", hash_password("pw"), "advertiser", "A")
        cre = create_user(test_conn, "nc@x.com", hash_password("pw"), "creator", "C")
        scores = {"embedding_score": 0.5, "audience_score": 0.5, "budget_score": 0.5, "values_score": 0.5, "weighted_score": 0.5}
        match = create_match(test_conn, adv["id"], cre["id"], scores)
        neg = create_negotiation(test_conn, match["id"], adv["id"], cre["id"])
        assert neg["status"] == "in_progress"

        add_negotiation_round(test_conn, neg["id"], 1, {
            "advertiser_message": "Hello", "creator_message": "Hi",
            "audience_score": 0.6, "audience_feedback": "OK",
        })
        fetched = get_negotiation(test_conn, neg["id"])
        assert fetched["current_round"] == 1
        assert len(fetched["rounds"]) == 1


class TestUsageLimits:
    def test_free_limit(self, test_conn):
        user = create_user(test_conn, "limit@x.com", hash_password("pw"), "advertiser", "Limit")
        assert check_match_limit(test_conn, user["id"], 3) is True
        for _ in range(3):
            increment_match_usage(test_conn, user["id"])
        assert check_match_limit(test_conn, user["id"], 3) is False
