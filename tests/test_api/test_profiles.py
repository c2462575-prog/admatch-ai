"""Test profile API endpoints."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


def _register(client, email, role):
    resp = client.post("/api/auth/register", json={
        "email": email, "password": "test123",
        "role": role, "display_name": f"Test {role}",
    })
    return resp.json()["access_token"]


class TestAdvertiserProfile:
    def test_create_profile(self, client):
        token = _register(client, "adv@test.com", "advertiser")
        resp = client.put("/api/advertisers/profile",
            json={"industry": "technology", "description": "Test brand", "budget_value": 100000, "values": ["innovation"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["industry"] == "technology"
        assert resp.json()["budget_value"] == 100000

    def test_get_profile(self, client):
        token = _register(client, "adv2@test.com", "advertiser")
        client.put("/api/advertisers/profile",
            json={"industry": "beauty", "description": "Beauty brand"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.get("/api/advertisers/profile", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["industry"] == "beauty"

    def test_creator_cannot_access_advertiser_profile(self, client):
        token = _register(client, "creator_blocked@test.com", "creator")
        resp = client.put("/api/advertisers/profile",
            json={"industry": "tech"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403


class TestCreatorProfile:
    def test_create_profile(self, client):
        token = _register(client, "creator@test.com", "creator")
        resp = client.put("/api/creators/profile",
            json={"niche": "technology", "description": "Tech channel", "follower_count": 50000,
                  "engagement_rate": 0.05, "min_fee": 10000, "max_fee": 50000, "values": ["authenticity"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["niche"] == "technology"
        assert resp.json()["follower_count"] == 50000

    def test_get_profile(self, client):
        token = _register(client, "creator2@test.com", "creator")
        client.put("/api/creators/profile",
            json={"niche": "lifestyle", "follower_count": 30000},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.get("/api/creators/profile", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["niche"] == "lifestyle"

    def test_advertiser_cannot_access_creator_profile(self, client):
        token = _register(client, "adv_blocked@test.com", "advertiser")
        resp = client.put("/api/creators/profile",
            json={"niche": "tech"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 403
