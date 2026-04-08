"""Test pricing API endpoints (public, no auth needed)."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestPriceEstimate:
    def test_default_params(self, client):
        resp = client.get("/api/pricing/estimate")
        assert resp.status_code == 200
        data = resp.json()
        assert "base_price" in data
        assert "suggested_range" in data

    def test_custom_params(self, client):
        resp = client.get("/api/pricing/estimate", params={
            "followers": 100000, "engagement_rate": 0.08, "category": "tech",
        })
        assert resp.status_code == 200
        assert resp.json()["base_price"] > 0

    def test_tech_premium(self, client):
        lifestyle = client.get("/api/pricing/estimate", params={
            "followers": 50000, "engagement_rate": 0.05, "category": "lifestyle",
        }).json()
        tech = client.get("/api/pricing/estimate", params={
            "followers": 50000, "engagement_rate": 0.05, "category": "tech",
        }).json()
        assert tech["base_price"] >= lifestyle["base_price"]


class TestRoiEstimate:
    def test_basic(self, client):
        resp = client.get("/api/pricing/roi", params={
            "price": 5000, "expected_reach": 50000, "conversion_rate": 0.02,
        })
        assert resp.status_code == 200
        data = resp.json()
        assert data["estimated_conversions"] == 1000
        assert data["cost_per_conversion"] == 5.0
