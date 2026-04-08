"""Test referral system."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../.."))

from core.database import create_user, create_referral_code, use_referral_code, get_referral_stats
from core.security import hash_password


class TestReferralSystem:
    def test_create_referral_code(self, test_conn):
        user = create_user(test_conn, "ref@x.com", hash_password("pw"), "advertiser", "Ref")
        code = create_referral_code(test_conn, user["id"])
        assert len(code) == 8
        assert code == code.upper()

    def test_same_user_gets_same_code(self, test_conn):
        user = create_user(test_conn, "same@x.com", hash_password("pw"), "creator", "Same")
        code1 = create_referral_code(test_conn, user["id"])
        code2 = create_referral_code(test_conn, user["id"])
        assert code1 == code2

    def test_use_referral_code(self, test_conn):
        referrer = create_user(test_conn, "r1@x.com", hash_password("pw"), "advertiser", "R1")
        code = create_referral_code(test_conn, referrer["id"])
        new_user = create_user(test_conn, "n1@x.com", hash_password("pw"), "creator", "N1")
        result = use_referral_code(test_conn, code, new_user["id"])
        assert result is True

    def test_cannot_use_own_code(self, test_conn):
        user = create_user(test_conn, "self@x.com", hash_password("pw"), "advertiser", "Self")
        code = create_referral_code(test_conn, user["id"])
        result = use_referral_code(test_conn, code, user["id"])
        assert result is False

    def test_invalid_code_fails(self, test_conn):
        user = create_user(test_conn, "bad@x.com", hash_password("pw"), "creator", "Bad")
        result = use_referral_code(test_conn, "INVALID1", user["id"])
        assert result is False

    def test_referral_stats(self, test_conn):
        referrer = create_user(test_conn, "rs@x.com", hash_password("pw"), "advertiser", "RS")
        code = create_referral_code(test_conn, referrer["id"])
        new_user = create_user(test_conn, "ns@x.com", hash_password("pw"), "creator", "NS")
        use_referral_code(test_conn, code, new_user["id"])
        stats = get_referral_stats(test_conn, referrer["id"])
        assert stats["total_referrals"] == 1
        assert stats["bonus_matches_earned"] == 2

    def test_referral_grants_bonus_matches(self, test_conn):
        referrer = create_user(test_conn, "bonus@x.com", hash_password("pw"), "advertiser", "Bonus")
        # Set initial usage to 2
        test_conn.execute("UPDATE users SET matches_used_this_month = 2 WHERE id = ?", (referrer["id"],))
        code = create_referral_code(test_conn, referrer["id"])
        new_user = create_user(test_conn, "nb@x.com", hash_password("pw"), "creator", "NB")
        use_referral_code(test_conn, code, new_user["id"])
        row = test_conn.execute("SELECT matches_used_this_month FROM users WHERE id = ?", (referrer["id"],)).fetchone()
        assert row[0] == 0  # 2 - 2 bonus = 0
