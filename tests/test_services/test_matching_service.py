"""Test matching service: keyword similarity and partial scores."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from services.matching_service import _keyword_similarity, _compute_partial_scores
from engine.matching import MatchingEngine


class TestKeywordSimilarity:
    def test_identical_content_high_score(self):
        adv = {"description": "tech startup cloud platform innovation", "industry": "technology",
               "target_audience": "developers", "campaign_goal": "user_acquisition", "values": ["innovation"]}
        creator = {"description": "tech startup cloud reviews for developers", "niche": "technology",
                   "content_style": ["tech_review"], "values": ["innovation"]}
        score = _keyword_similarity(adv, creator)
        assert score > 0.3

    def test_unrelated_content_low_score(self):
        adv = {"description": "organic skincare beauty natural ingredients", "industry": "beauty",
               "target_audience": "women", "campaign_goal": "brand_awareness", "values": ["natural"]}
        creator = {"description": "programming tutorials python javascript", "niche": "technology",
                   "content_style": ["coding"], "values": ["technical_accuracy"]}
        score = _keyword_similarity(adv, creator)
        assert score < 0.15

    def test_empty_descriptions_returns_default(self):
        adv = {"description": "", "industry": "", "target_audience": "", "campaign_goal": "", "values": []}
        creator = {"description": "", "niche": "", "content_style": [], "values": []}
        score = _keyword_similarity(adv, creator)
        assert score == 0.3  # neutral default

    def test_partial_overlap(self):
        adv = {"description": "coffee lifestyle urban culture brand", "industry": "food_beverage",
               "target_audience": "urban_professionals", "campaign_goal": "brand_awareness",
               "values": ["craftsmanship", "community"]}
        creator = {"description": "lifestyle coffee culture city exploration", "niche": "lifestyle",
                   "content_style": ["lifestyle", "coffee"], "values": ["authenticity", "quality"]}
        score = _keyword_similarity(adv, creator)
        assert 0.1 < score < 0.8  # meaningful overlap but not identical

    def test_values_overlap_counts(self):
        adv = {"description": "brand", "industry": "", "target_audience": "", "campaign_goal": "",
               "values": ["sustainability", "authenticity", "quality"]}
        creator = {"description": "creator", "niche": "", "content_style": [],
                   "values": ["sustainability", "authenticity"]}
        score = _keyword_similarity(adv, creator)
        assert score > 0.1


class TestComputePartialScores:
    def test_returns_all_required_keys(self):
        engine = MatchingEngine()
        adv = {"id": "a1", "target_audience": "tech_professionals", "budget_value": 100000, "values": ["innovation"]}
        creator = {"id": "c1", "content_style": ["tech_review"], "min_fee": 50000, "max_fee": 120000, "values": ["innovation"]}
        audience = {"acceptance_threshold": 0.35}
        scores = _compute_partial_scores(engine, adv, creator, audience)
        assert "embedding_score" in scores
        assert "audience_score" in scores
        assert "budget_score" in scores
        assert "values_score" in scores
        assert "weighted_score" in scores

    def test_weighted_score_within_range(self):
        engine = MatchingEngine()
        adv = {"id": "a2", "target_audience": "general", "budget_value": 50000, "values": ["quality"]}
        creator = {"id": "c2", "content_style": ["lifestyle"], "min_fee": 10000, "max_fee": 80000, "values": ["quality"]}
        audience = {"acceptance_threshold": 0.35}
        scores = _compute_partial_scores(engine, adv, creator, audience)
        assert 0 <= scores["weighted_score"] <= 1
        assert 0 <= scores["embedding_score"] <= 1

    def test_embedding_score_not_zero(self):
        """Verify fallback provides non-zero embedding score."""
        engine = MatchingEngine()
        adv = {"id": "a3", "description": "coffee brand", "target_audience": "urban_professionals",
               "budget_value": 75000, "values": ["craftsmanship"], "industry": "food"}
        creator = {"id": "c3", "description": "coffee lifestyle", "content_style": ["coffee"],
                   "niche": "lifestyle", "min_fee": 30000, "max_fee": 80000, "values": ["authenticity"]}
        audience = {"acceptance_threshold": 0.35}
        scores = _compute_partial_scores(engine, adv, creator, audience)
        assert scores["embedding_score"] > 0
