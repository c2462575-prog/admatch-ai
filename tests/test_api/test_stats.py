"""Test platform stats endpoint."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestPlatformStats:
    def test_stats_returns_counts(self, client):
        # Register some users first
        client.post("/api/auth/register", json={
            "email": "adv@stats.com", "password": "test123",
            "role": "advertiser", "display_name": "Adv",
        })
        client.post("/api/auth/register", json={
            "email": "cre@stats.com", "password": "test123",
            "role": "creator", "display_name": "Cre",
        })
        resp = client.get("/api/stats/platform")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_advertisers"] >= 1
        assert data["total_creators"] >= 1
        assert "total_matches" in data
        assert "successful_negotiations" in data

    def test_stats_no_auth_needed(self, client):
        resp = client.get("/api/stats/platform")
        assert resp.status_code == 200
