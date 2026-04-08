"""Public explore endpoint — no auth required, for top-of-funnel discovery."""
from fastapi import APIRouter, Depends
from core.dependencies import get_db_conn

router = APIRouter()


@router.get("/creators")
def explore_creators(niche: str = "", limit: int = 20, conn=Depends(get_db_conn)):
    """Public creator listing with sanitized data (no fees, no contact info)."""
    query = """
        SELECT u.display_name, cp.niche, cp.description, cp.follower_count,
               cp.engagement_rate, cp.content_style_json, cp.values_json
        FROM users u JOIN creator_profiles cp ON u.id = cp.user_id
        WHERE u.is_active = 1 AND u.role = 'creator' AND cp.niche != ''
    """
    params = []
    if niche:
        query += " AND cp.niche = ?"
        params.append(niche)
    query += " ORDER BY cp.follower_count DESC LIMIT ?"
    params.append(limit)

    rows = conn.execute(query, params).fetchall()
    import json
    results = []
    for r in rows:
        results.append({
            "display_name": r[0],
            "niche": r[1],
            "description": r[2][:150] + "..." if len(r[2]) > 150 else r[2],
            "follower_count": r[3],
            "engagement_rate": r[4],
            "content_style": json.loads(r[5]) if r[5] else [],
            "values": json.loads(r[6]) if r[6] else [],
        })
    return {"creators": results, "total": len(results)}


@router.get("/niches")
def list_niches(conn=Depends(get_db_conn)):
    """List all available creator niches with counts."""
    rows = conn.execute("""
        SELECT cp.niche, COUNT(*) as cnt
        FROM creator_profiles cp JOIN users u ON cp.user_id = u.id
        WHERE u.is_active = 1 AND cp.niche != ''
        GROUP BY cp.niche ORDER BY cnt DESC
    """).fetchall()
    return [{"niche": r[0], "count": r[1]} for r in rows]
