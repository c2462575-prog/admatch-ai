"""SQLite database: schema creation and CRUD operations."""
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from contextlib import contextmanager
from core.config import DATABASE_PATH

DDL = """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('advertiser', 'creator')),
    display_name TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at TEXT NOT NULL DEFAULT (datetime('now')),
    is_active INTEGER NOT NULL DEFAULT 1,
    plan TEXT NOT NULL DEFAULT 'free' CHECK(plan IN ('free', 'basic', 'pro')),
    matches_used_this_month INTEGER NOT NULL DEFAULT 0,
    matches_reset_date TEXT
);

CREATE TABLE IF NOT EXISTS advertiser_profiles (
    user_id TEXT PRIMARY KEY REFERENCES users(id),
    industry TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    budget_range TEXT DEFAULT 'medium',
    budget_value INTEGER DEFAULT 0,
    target_audience TEXT DEFAULT '',
    values_json TEXT NOT NULL DEFAULT '[]',
    campaign_goal TEXT DEFAULT '',
    ai_profile_json TEXT,
    embedding_description TEXT,
    embedding_vector BLOB,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS creator_profiles (
    user_id TEXT PRIMARY KEY REFERENCES users(id),
    niche TEXT NOT NULL DEFAULT '',
    description TEXT NOT NULL DEFAULT '',
    follower_count INTEGER NOT NULL DEFAULT 0,
    engagement_rate REAL NOT NULL DEFAULT 0.0,
    content_style_json TEXT NOT NULL DEFAULT '[]',
    min_fee INTEGER NOT NULL DEFAULT 0,
    max_fee INTEGER NOT NULL DEFAULT 0,
    values_json TEXT NOT NULL DEFAULT '[]',
    audience_description TEXT DEFAULT '',
    audience_acceptance_threshold REAL DEFAULT 0.35,
    audience_sensitivity_json TEXT DEFAULT '[]',
    audience_rejection_triggers_json TEXT DEFAULT '[]',
    ai_profile_json TEXT,
    embedding_description TEXT,
    embedding_vector BLOB,
    updated_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS matches (
    id TEXT PRIMARY KEY,
    advertiser_id TEXT NOT NULL REFERENCES users(id),
    creator_id TEXT NOT NULL REFERENCES users(id),
    embedding_score REAL NOT NULL DEFAULT 0,
    audience_score REAL NOT NULL DEFAULT 0,
    budget_score REAL NOT NULL DEFAULT 0,
    values_score REAL NOT NULL DEFAULT 0,
    weighted_score REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK(status IN ('pending','viewed_by_advertiser','viewed_by_creator','negotiation_started','completed','expired')),
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(advertiser_id, creator_id)
);

CREATE TABLE IF NOT EXISTS negotiations (
    id TEXT PRIMARY KEY,
    match_id TEXT NOT NULL REFERENCES matches(id),
    advertiser_id TEXT NOT NULL REFERENCES users(id),
    creator_id TEXT NOT NULL REFERENCES users(id),
    status TEXT NOT NULL DEFAULT 'in_progress'
        CHECK(status IN ('in_progress','success','failed','audience_rejected')),
    current_round INTEGER NOT NULL DEFAULT 0,
    final_price INTEGER DEFAULT 0,
    summary TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    completed_at TEXT
);

CREATE TABLE IF NOT EXISTS negotiation_rounds (
    id TEXT PRIMARY KEY,
    negotiation_id TEXT NOT NULL REFERENCES negotiations(id),
    round_num INTEGER NOT NULL CHECK(round_num BETWEEN 1 AND 3),
    advertiser_message TEXT NOT NULL DEFAULT '',
    creator_message TEXT NOT NULL DEFAULT '',
    audience_score REAL,
    audience_feedback TEXT,
    intervention_warning TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(negotiation_id, round_num)
);

CREATE TABLE IF NOT EXISTS referrals (
    id TEXT PRIMARY KEY,
    referrer_id TEXT NOT NULL REFERENCES users(id),
    referral_code TEXT UNIQUE NOT NULL,
    referred_user_id TEXT REFERENCES users(id),
    bonus_granted INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    used_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_matches_advertiser ON matches(advertiser_id, weighted_score DESC);
CREATE INDEX IF NOT EXISTS idx_matches_creator ON matches(creator_id, weighted_score DESC);
CREATE INDEX IF NOT EXISTS idx_negotiations_match ON negotiations(match_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_referrals_code ON referrals(referral_code);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def new_id() -> str:
    return str(uuid.uuid4())


@contextmanager
def get_db(db_path: str | None = None):
    """Context manager yielding a sqlite3 connection with row_factory."""
    conn = sqlite3.connect(db_path or DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: str | None = None):
    """Create all tables."""
    with get_db(db_path) as conn:
        conn.executescript(DDL)


# ── User CRUD ───────────────────────────────────────────

def create_user(conn, email: str, password_hash: str, role: str, display_name: str) -> dict:
    uid = new_id()
    now = _now()
    conn.execute(
        "INSERT INTO users (id, email, password_hash, role, display_name, created_at, updated_at) VALUES (?,?,?,?,?,?,?)",
        (uid, email, password_hash, role, display_name, now, now),
    )
    return {"id": uid, "email": email, "role": role, "display_name": display_name}


def get_user_by_email(conn, email: str) -> dict | None:
    row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    return dict(row) if row else None


def get_user_by_id(conn, user_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    return dict(row) if row else None


# ── Advertiser Profile CRUD ─────────────────────────────

def upsert_advertiser_profile(conn, user_id: str, data: dict) -> dict:
    now = _now()
    values_json = json.dumps(data.get("values", []), ensure_ascii=False)
    conn.execute("""
        INSERT INTO advertiser_profiles (user_id, industry, description, budget_range, budget_value,
            target_audience, values_json, campaign_goal, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            industry=excluded.industry, description=excluded.description,
            budget_range=excluded.budget_range, budget_value=excluded.budget_value,
            target_audience=excluded.target_audience, values_json=excluded.values_json,
            campaign_goal=excluded.campaign_goal, updated_at=excluded.updated_at
    """, (user_id, data.get("industry", ""), data.get("description", ""),
          data.get("budget_range", "medium"), data.get("budget_value", 0),
          data.get("target_audience", ""), values_json,
          data.get("campaign_goal", ""), now))
    return get_advertiser_profile(conn, user_id)


def get_advertiser_profile(conn, user_id: str) -> dict | None:
    row = conn.execute(
        "SELECT u.*, ap.* FROM users u JOIN advertiser_profiles ap ON u.id = ap.user_id WHERE u.id = ?",
        (user_id,),
    ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["values"] = json.loads(d.pop("values_json", "[]"))
    return d


def get_all_advertiser_profiles(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT u.*, ap.* FROM users u JOIN advertiser_profiles ap ON u.id = ap.user_id WHERE u.is_active = 1"
    ).fetchall()
    results = []
    for row in rows:
        d = dict(row)
        d["values"] = json.loads(d.pop("values_json", "[]"))
        results.append(d)
    return results


# ── Creator Profile CRUD ────────────────────────────────

def upsert_creator_profile(conn, user_id: str, data: dict) -> dict:
    now = _now()
    conn.execute("""
        INSERT INTO creator_profiles (user_id, niche, description, follower_count, engagement_rate,
            content_style_json, min_fee, max_fee, values_json, audience_description,
            audience_acceptance_threshold, audience_sensitivity_json,
            audience_rejection_triggers_json, updated_at)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ON CONFLICT(user_id) DO UPDATE SET
            niche=excluded.niche, description=excluded.description,
            follower_count=excluded.follower_count, engagement_rate=excluded.engagement_rate,
            content_style_json=excluded.content_style_json, min_fee=excluded.min_fee,
            max_fee=excluded.max_fee, values_json=excluded.values_json,
            audience_description=excluded.audience_description,
            audience_acceptance_threshold=excluded.audience_acceptance_threshold,
            audience_sensitivity_json=excluded.audience_sensitivity_json,
            audience_rejection_triggers_json=excluded.audience_rejection_triggers_json,
            updated_at=excluded.updated_at
    """, (user_id, data.get("niche", ""), data.get("description", ""),
          data.get("follower_count", 0), data.get("engagement_rate", 0.0),
          json.dumps(data.get("content_style", []), ensure_ascii=False),
          data.get("min_fee", 0), data.get("max_fee", 0),
          json.dumps(data.get("values", []), ensure_ascii=False),
          data.get("audience_description", ""),
          data.get("audience_acceptance_threshold", 0.35),
          json.dumps(data.get("audience_sensitivity_factors", []), ensure_ascii=False),
          json.dumps(data.get("audience_rejection_triggers", []), ensure_ascii=False),
          now))
    return get_creator_profile(conn, user_id)


def get_creator_profile(conn, user_id: str) -> dict | None:
    row = conn.execute(
        "SELECT u.*, cp.* FROM users u JOIN creator_profiles cp ON u.id = cp.user_id WHERE u.id = ?",
        (user_id,),
    ).fetchone()
    if not row:
        return None
    d = dict(row)
    d["values"] = json.loads(d.pop("values_json", "[]"))
    d["content_style"] = json.loads(d.pop("content_style_json", "[]"))
    d["audience_sensitivity_factors"] = json.loads(d.pop("audience_sensitivity_json", "[]"))
    d["audience_rejection_triggers"] = json.loads(d.pop("audience_rejection_triggers_json", "[]"))
    return d


def get_all_creator_profiles(conn) -> list[dict]:
    rows = conn.execute(
        "SELECT u.*, cp.* FROM users u JOIN creator_profiles cp ON u.id = cp.user_id WHERE u.is_active = 1"
    ).fetchall()
    results = []
    for row in rows:
        d = dict(row)
        d["values"] = json.loads(d.pop("values_json", "[]"))
        d["content_style"] = json.loads(d.pop("content_style_json", "[]"))
        d["audience_sensitivity_factors"] = json.loads(d.pop("audience_sensitivity_json", "[]"))
        d["audience_rejection_triggers"] = json.loads(d.pop("audience_rejection_triggers_json", "[]"))
        results.append(d)
    return results


# ── Match CRUD ──────────────────────────────────────────

def create_match(conn, advertiser_id: str, creator_id: str, scores: dict) -> dict:
    mid = new_id()
    conn.execute("""
        INSERT INTO matches (id, advertiser_id, creator_id, embedding_score, audience_score,
            budget_score, values_score, weighted_score)
        VALUES (?,?,?,?,?,?,?,?)
        ON CONFLICT(advertiser_id, creator_id) DO UPDATE SET
            embedding_score=excluded.embedding_score, audience_score=excluded.audience_score,
            budget_score=excluded.budget_score, values_score=excluded.values_score,
            weighted_score=excluded.weighted_score, status='pending',
            created_at=datetime('now')
    """, (mid, advertiser_id, creator_id,
          scores.get("embedding_score", 0), scores.get("audience_score", 0),
          scores.get("budget_score", 0), scores.get("values_score", 0),
          scores.get("weighted_score", 0)))
    return {"id": mid, **scores}


def get_matches_for_user(conn, user_id: str, role: str, limit: int = 20) -> list[dict]:
    col = "advertiser_id" if role == "advertiser" else "creator_id"
    partner_col = "creator_id" if role == "advertiser" else "advertiser_id"
    rows = conn.execute(f"""
        SELECT m.*, u.display_name as partner_name
        FROM matches m JOIN users u ON m.{partner_col} = u.id
        WHERE m.{col} = ? ORDER BY m.weighted_score DESC LIMIT ?
    """, (user_id, limit)).fetchall()
    return [dict(r) for r in rows]


def get_match_by_id(conn, match_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM matches WHERE id = ?", (match_id,)).fetchone()
    return dict(row) if row else None


# ── Negotiation CRUD ────────────────────────────────────

def create_negotiation(conn, match_id: str, advertiser_id: str, creator_id: str) -> dict:
    nid = new_id()
    conn.execute(
        "INSERT INTO negotiations (id, match_id, advertiser_id, creator_id) VALUES (?,?,?,?)",
        (nid, match_id, advertiser_id, creator_id),
    )
    conn.execute("UPDATE matches SET status = 'negotiation_started' WHERE id = ?", (match_id,))
    return {"id": nid, "match_id": match_id, "status": "in_progress", "current_round": 0}


def add_negotiation_round(conn, negotiation_id: str, round_num: int, data: dict) -> dict:
    rid = new_id()
    conn.execute("""
        INSERT INTO negotiation_rounds (id, negotiation_id, round_num, advertiser_message,
            creator_message, audience_score, audience_feedback, intervention_warning)
        VALUES (?,?,?,?,?,?,?,?)
    """, (rid, negotiation_id, round_num,
          data.get("advertiser_message", ""), data.get("creator_message", ""),
          data.get("audience_score"), data.get("audience_feedback"),
          data.get("intervention_warning")))
    conn.execute(
        "UPDATE negotiations SET current_round = ? WHERE id = ?",
        (round_num, negotiation_id),
    )
    return {"id": rid, "round_num": round_num, **data}


def complete_negotiation(conn, negotiation_id: str, status: str, final_price: int = 0, summary: str = ""):
    conn.execute(
        "UPDATE negotiations SET status=?, final_price=?, summary=?, completed_at=datetime('now') WHERE id=?",
        (status, final_price, summary, negotiation_id),
    )


def get_negotiation(conn, negotiation_id: str) -> dict | None:
    row = conn.execute("SELECT * FROM negotiations WHERE id = ?", (negotiation_id,)).fetchone()
    if not row:
        return None
    d = dict(row)
    rounds = conn.execute(
        "SELECT * FROM negotiation_rounds WHERE negotiation_id = ? ORDER BY round_num",
        (negotiation_id,),
    ).fetchall()
    d["rounds"] = [dict(r) for r in rounds]
    return d


def get_negotiations_for_user(conn, user_id: str) -> list[dict]:
    rows = conn.execute("""
        SELECT n.*, u1.display_name as advertiser_name, u2.display_name as creator_name
        FROM negotiations n
        JOIN users u1 ON n.advertiser_id = u1.id
        JOIN users u2 ON n.creator_id = u2.id
        WHERE n.advertiser_id = ? OR n.creator_id = ?
        ORDER BY n.created_at DESC
    """, (user_id, user_id)).fetchall()
    return [dict(r) for r in rows]


# ── Usage tracking ──────────────────────────────────────

def increment_match_usage(conn, user_id: str):
    conn.execute(
        "UPDATE users SET matches_used_this_month = matches_used_this_month + 1 WHERE id = ?",
        (user_id,),
    )


def check_match_limit(conn, user_id: str, free_limit: int) -> bool:
    """Returns True if user can still run matches."""
    user = get_user_by_id(conn, user_id)
    if not user:
        return False
    if user["plan"] != "free":
        return True
    return user["matches_used_this_month"] < free_limit


def update_advertiser_embedding(conn, user_id: str, description: str, vector: bytes):
    conn.execute(
        "UPDATE advertiser_profiles SET embedding_description=?, embedding_vector=? WHERE user_id=?",
        (description, vector, user_id),
    )


def update_creator_embedding(conn, user_id: str, description: str, vector: bytes):
    conn.execute(
        "UPDATE creator_profiles SET embedding_description=?, embedding_vector=? WHERE user_id=?",
        (description, vector, user_id),
    )


# ── Referral system ─────────────────────────────────────

REFERRAL_BONUS_MATCHES = 2


def create_referral_code(conn, user_id: str) -> str:
    """Generate a unique referral code for a user. Returns existing if already has one."""
    row = conn.execute("SELECT referral_code FROM referrals WHERE referrer_id = ? AND referred_user_id IS NULL", (user_id,)).fetchone()
    if row:
        return row[0]
    import hashlib
    code = hashlib.sha256(f"{user_id}-{_now()}".encode()).hexdigest()[:8].upper()
    rid = new_id()
    conn.execute("INSERT INTO referrals (id, referrer_id, referral_code) VALUES (?,?,?)", (rid, user_id, code))
    return code


def use_referral_code(conn, code: str, new_user_id: str) -> bool:
    """Apply a referral code for a new user. Returns True if successful."""
    row = conn.execute("SELECT id, referrer_id FROM referrals WHERE referral_code = ? AND referred_user_id IS NULL", (code,)).fetchone()
    if not row:
        return False
    referral_id, referrer_id = row[0], row[1]
    if referrer_id == new_user_id:
        return False  # can't refer yourself
    conn.execute("UPDATE referrals SET referred_user_id=?, used_at=datetime('now'), bonus_granted=1 WHERE id=?", (new_user_id, referral_id))
    # Grant bonus matches to referrer
    conn.execute(
        "UPDATE users SET matches_used_this_month = MAX(0, matches_used_this_month - ?) WHERE id = ?",
        (REFERRAL_BONUS_MATCHES, referrer_id),
    )
    return True


def get_referral_stats(conn, user_id: str) -> dict:
    """Get referral stats for a user."""
    code_row = conn.execute("SELECT referral_code FROM referrals WHERE referrer_id = ? LIMIT 1", (user_id,)).fetchone()
    total = conn.execute("SELECT COUNT(*) FROM referrals WHERE referrer_id = ? AND referred_user_id IS NOT NULL", (user_id,)).fetchone()[0]
    bonus = total * REFERRAL_BONUS_MATCHES
    return {
        "referral_code": code_row[0] if code_row else None,
        "total_referrals": total,
        "bonus_matches_earned": bonus,
    }
