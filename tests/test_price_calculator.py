"""Tests for price_calculator module"""
import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.price_calculator import calculate_creator_price, estimate_roi


class TestCalculateCreatorPrice:
    def test_returns_dict(self):
        result = calculate_creator_price(10000, 0.05, "lifestyle")
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = calculate_creator_price(10000, 0.05, "lifestyle")
        assert "base_price" in result
        assert "suggested_range" in result

    def test_more_followers_higher_price(self):
        small = calculate_creator_price(1000, 0.05, "lifestyle")
        large = calculate_creator_price(100000, 0.05, "lifestyle")
        assert large["base_price"] > small["base_price"]

    def test_higher_engagement_higher_price(self):
        low = calculate_creator_price(10000, 0.01, "lifestyle")
        high = calculate_creator_price(10000, 0.10, "lifestyle")
        assert high["base_price"] > low["base_price"]

    def test_tech_category_premium(self):
        lifestyle = calculate_creator_price(10000, 0.05, "lifestyle")
        tech = calculate_creator_price(10000, 0.05, "tech")
        assert tech["base_price"] >= lifestyle["base_price"]


class TestEstimateRoi:
    def test_returns_dict(self):
        result = estimate_roi(5000, 50000, 0.02)
        assert isinstance(result, dict)

    def test_has_required_keys(self):
        result = estimate_roi(5000, 50000, 0.02)
        assert "estimated_conversions" in result
        assert "cost_per_conversion" in result
        assert "roi_score" in result

    def test_higher_reach_better_roi(self):
        low = estimate_roi(5000, 10000, 0.02)
        high = estimate_roi(5000, 100000, 0.02)
        assert high["roi_score"] > low["roi_score"]

    def test_zero_price_raises(self):
        with pytest.raises(ValueError):
            estimate_roi(0, 50000, 0.02)
