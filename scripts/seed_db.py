"""Seed the database with test data from data/scenarios.py."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from core.database import init_db, get_db, create_user, upsert_advertiser_profile, upsert_creator_profile
from core.security import hash_password
from data.scenarios import ADVERTISERS, CREATORS, AUDIENCES


def seed():
    init_db()
    with get_db() as conn:
        # Seed advertisers
        for key, adv in ADVERTISERS.items():
            email = f"{key}@demo.admatch.ai"
            existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                print(f"  Advertiser {key} already exists, skipping")
                continue
            user = create_user(conn, email, hash_password("demo123"), "advertiser", adv["name"])
            upsert_advertiser_profile(conn, user["id"], adv)
            print(f"  Created advertiser: {adv['name']} ({email})")

        # Seed creators
        for key, creator in CREATORS.items():
            email = f"{key}@demo.admatch.ai"
            existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if existing:
                print(f"  Creator {key} already exists, skipping")
                continue
            audience = AUDIENCES.get(f"{key}_audience", {})
            user = create_user(conn, email, hash_password("demo123"), "creator", creator["name"])
            creator_data = {**creator}
            creator_data["audience_description"] = audience.get("description", "")
            creator_data["audience_acceptance_threshold"] = audience.get("acceptance_threshold", 0.35)
            creator_data["audience_sensitivity_factors"] = audience.get("sensitivity_factors", [])
            creator_data["audience_rejection_triggers"] = audience.get("rejection_triggers", [])
            upsert_creator_profile(conn, user["id"], creator_data)
            print(f"  Created creator: {creator['name']} ({email})")

    print("Seed complete!")


if __name__ == "__main__":
    seed()
