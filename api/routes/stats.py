"""Platform statistics endpoints."""
from fastapi import APIRouter, Depends
from core.dependencies import get_db_conn, get_current_user

router = APIRouter()


@router.get("/platform")
def platform_stats(conn=Depends(get_db_conn)):
    """Public stats for landing page social proof."""
    advertisers = conn.execute("SELECT COUNT(*) FROM users WHERE role='advertiser' AND is_active=1").fetchone()[0]
    creators = conn.execute("SELECT COUNT(*) FROM users WHERE role='creator' AND is_active=1").fetchone()[0]
    matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    successful = conn.execute("SELECT COUNT(*) FROM negotiations WHERE status='success'").fetchone()[0]
    return {
        "total_advertisers": advertisers,
        "total_creators": creators,
        "total_matches": matches,
        "successful_negotiations": successful,
    }


@router.get("/admin/analytics")
def admin_analytics(conn=Depends(get_db_conn)):
    """Detailed analytics for founder/admin dashboard."""
    # User metrics
    total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    advertisers = conn.execute("SELECT COUNT(*) FROM users WHERE role='advertiser'").fetchone()[0]
    creators = conn.execute("SELECT COUNT(*) FROM users WHERE role='creator'").fetchone()[0]
    free_users = conn.execute("SELECT COUNT(*) FROM users WHERE plan='free'").fetchone()[0]
    paid_users = total_users - free_users

    # Profile completion
    adv_profiles = conn.execute("SELECT COUNT(*) FROM advertiser_profiles WHERE industry != ''").fetchone()[0]
    creator_profiles = conn.execute("SELECT COUNT(*) FROM creator_profiles WHERE niche != ''").fetchone()[0]

    # Matching metrics
    total_matches = conn.execute("SELECT COUNT(*) FROM matches").fetchone()[0]
    avg_score = conn.execute("SELECT COALESCE(AVG(weighted_score), 0) FROM matches").fetchone()[0]
    high_matches = conn.execute("SELECT COUNT(*) FROM matches WHERE weighted_score >= 0.6").fetchone()[0]

    # Negotiation metrics
    total_neg = conn.execute("SELECT COUNT(*) FROM negotiations").fetchone()[0]
    success_neg = conn.execute("SELECT COUNT(*) FROM negotiations WHERE status='success'").fetchone()[0]
    failed_neg = conn.execute("SELECT COUNT(*) FROM negotiations WHERE status='failed'").fetchone()[0]
    rejected_neg = conn.execute("SELECT COUNT(*) FROM negotiations WHERE status='audience_rejected'").fetchone()[0]
    in_progress_neg = conn.execute("SELECT COUNT(*) FROM negotiations WHERE status='in_progress'").fetchone()[0]

    # Referral metrics
    total_referrals = conn.execute("SELECT COUNT(*) FROM referrals WHERE referred_user_id IS NOT NULL").fetchone()[0]

    # Revenue potential (paid conversion)
    conversion_rate = (paid_users / total_users * 100) if total_users > 0 else 0
    negotiation_success_rate = (success_neg / total_neg * 100) if total_neg > 0 else 0

    return {
        "users": {
            "total": total_users,
            "advertisers": advertisers,
            "creators": creators,
            "free": free_users,
            "paid": paid_users,
            "conversion_rate": round(conversion_rate, 1),
        },
        "profiles": {
            "advertiser_completed": adv_profiles,
            "creator_completed": creator_profiles,
            "advertiser_completion_rate": round(adv_profiles / advertisers * 100, 1) if advertisers > 0 else 0,
            "creator_completion_rate": round(creator_profiles / creators * 100, 1) if creators > 0 else 0,
        },
        "matching": {
            "total_matches": total_matches,
            "avg_score": round(avg_score, 4),
            "high_quality_matches": high_matches,
        },
        "negotiations": {
            "total": total_neg,
            "success": success_neg,
            "failed": failed_neg,
            "audience_rejected": rejected_neg,
            "in_progress": in_progress_neg,
            "success_rate": round(negotiation_success_rate, 1),
        },
        "growth": {
            "referrals_completed": total_referrals,
        },
    }


@router.get("/admin/errors")
def admin_errors(limit: int = 20):
    """Recent error log for admin debugging."""
    from core.error_tracker import get_recent_errors
    return get_recent_errors(limit)


@router.get("/admin/error-summary")
def admin_error_summary():
    """Error summary by source."""
    from core.error_tracker import get_error_summary
    return get_error_summary()
