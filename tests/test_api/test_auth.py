"""Test auth API endpoints."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))


class TestRegister:
    def test_register_advertiser(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "test@example.com",
            "password": "test123",
            "role": "advertiser",
            "display_name": "Test Advertiser",
        })
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["role"] == "advertiser"
        assert data["user"]["email"] == "test@example.com"

    def test_register_creator(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "creator@example.com",
            "password": "test123",
            "role": "creator",
            "display_name": "Test Creator",
        })
        assert resp.status_code == 201
        assert resp.json()["user"]["role"] == "creator"

    def test_register_duplicate_email(self, client):
        client.post("/api/auth/register", json={
            "email": "dup@example.com", "password": "test123",
            "role": "advertiser", "display_name": "First",
        })
        resp = client.post("/api/auth/register", json={
            "email": "dup@example.com", "password": "test456",
            "role": "creator", "display_name": "Second",
        })
        assert resp.status_code == 409

    def test_register_invalid_role(self, client):
        resp = client.post("/api/auth/register", json={
            "email": "bad@example.com", "password": "test123",
            "role": "admin", "display_name": "Bad",
        })
        assert resp.status_code == 422


class TestLogin:
    def test_login_success(self, client):
        client.post("/api/auth/register", json={
            "email": "login@example.com", "password": "pass123",
            "role": "advertiser", "display_name": "Login Test",
        })
        resp = client.post("/api/auth/login", json={
            "email": "login@example.com", "password": "pass123",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self, client):
        client.post("/api/auth/register", json={
            "email": "wrong@example.com", "password": "correct",
            "role": "advertiser", "display_name": "Wrong PW",
        })
        resp = client.post("/api/auth/login", json={
            "email": "wrong@example.com", "password": "incorrect",
        })
        assert resp.status_code == 401

    def test_login_nonexistent(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "nobody@example.com", "password": "test123",
        })
        assert resp.status_code == 401


class TestMe:
    def test_me_authenticated(self, client):
        reg = client.post("/api/auth/register", json={
            "email": "me@example.com", "password": "test123",
            "role": "advertiser", "display_name": "Me Test",
        }).json()
        token = reg["access_token"]
        resp = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@example.com"

    def test_me_no_token(self, client):
        resp = client.get("/api/auth/me")
        assert resp.status_code == 401

    def test_me_bad_token(self, client):
        resp = client.get("/api/auth/me", headers={"Authorization": "Bearer invalid"})
        assert resp.status_code == 401
