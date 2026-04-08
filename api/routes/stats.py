"""Public platform statistics endpoint."""
from fastapi import APIRouter, Depends
from core.dependencies import get_db_conn

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
