"""Test security module: JWT and password hashing."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.security import hash_password, verify_password, create_jwt, decode_jwt


class TestPasswordHashing:
    def test_hash_and_verify(self):
        pw = "mySecurePassword123"
        hashed = hash_password(pw)
        assert verify_password(pw, hashed) is True

    def test_wrong_password_fails(self):
        hashed = hash_password("correct")
        assert verify_password("wrong", hashed) is False

    def test_different_hashes_for_same_password(self):
        h1 = hash_password("same")
        h2 = hash_password("same")
        assert h1 != h2  # different salts

    def test_hash_format(self):
        hashed = hash_password("test")
        assert ":" in hashed
        salt, digest = hashed.split(":")
        assert len(salt) == 32  # hex of 16 bytes
        assert len(digest) == 64  # hex of sha256


class TestJWT:
    def test_create_and_decode(self):
        payload = {"sub": "user-123", "role": "advertiser"}
        token = create_jwt(payload)
        decoded = decode_jwt(token)
        assert decoded is not None
        assert decoded["sub"] == "user-123"
        assert decoded["role"] == "advertiser"

    def test_expired_token_rejected(self):
        # Temporarily monkey-patch expire to -1 minute
        import core.security as sec
        original = sec.JWT_EXPIRE_MINUTES
        sec.JWT_EXPIRE_MINUTES = -1
        token = create_jwt({"sub": "expired-user"})
        sec.JWT_EXPIRE_MINUTES = original
        assert decode_jwt(token) is None

    def test_tampered_token_rejected(self):
        token = create_jwt({"sub": "user-456"})
        parts = token.split(".")
        # Tamper with payload
        tampered = parts[0] + "." + parts[1] + "x" + "." + parts[2]
        assert decode_jwt(tampered) is None

    def test_invalid_format_rejected(self):
        assert decode_jwt("not.a.valid.token.at.all") is None
        assert decode_jwt("") is None
        assert decode_jwt("onlyone") is None

    def test_token_has_expiry(self):
        token = create_jwt({"sub": "test"})
        decoded = decode_jwt(token)
        assert "exp" in decoded
        assert decoded["exp"] > time.time()
