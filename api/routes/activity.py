"""Activity feed endpoint — recent platform and user events."""
from fastapi import APIRouter, Depends
from core.dependencies import get_db_conn, get_current_user

router = APIRouter()


@router.get("/feed")
def activity_feed(limit: int = 10, user: dict = Depends(get_current_user), conn=Depends(get_db_conn)):
    """Personal activity feed for the logged-in user."""
    user_id = user["id"]
    events = []

    # Recent matches
    matches = conn.execute("""
        SELECT m.weighted_score, m.created_at, u.display_name
        FROM matches m JOIN users u ON (
            CASE WHEN m.advertiser_id = ? THEN m.creator_id ELSE m.advertiser_id END
        ) = u.id
        WHERE m.advertiser_id = ? OR m.creator_id = ?
        ORDER BY m.created_at DESC LIMIT 5
    """, (user_id, user_id, user_id)).fetchall()

    for r in matches:
        events.append({
            "type": "match",
            "icon": "🤝",
            "text": f"與 {r[1]} 的匹配分數：{r[0]:.1%}" if r[0] else f"與 {r[2]} 完成配對",
            "detail": f"匹配分數 {r[0]:.1%}",
            "time": r[1],
            "partner": r[2],
        })

    # Recent negotiations
    negs = conn.execute("""
        SELECT n.status, n.created_at, n.completed_at, n.final_price,
               u1.display_name as adv_name, u2.display_name as cre_name
        FROM negotiations n
        JOIN users u1 ON n.advertiser_id = u1.id
        JOIN users u2 ON n.creator_id = u2.id
        WHERE n.advertiser_id = ? OR n.creator_id = ?
        ORDER BY n.created_at DESC LIMIT 5
    """, (user_id, user_id)).fetchall()

    status_text = {"in_progress": "談判進行中", "success": "合作達成", "failed": "談判未成功", "audience_rejected": "觀眾否決"}
    for r in negs:
        partner = r[5] if user["role"] == "advertiser" else r[4]
        events.append({
            "type": "negotiation",
            "icon": "💬" if r[0] == "in_progress" else "✅" if r[0] == "success" else "❌",
            "text": f"與 {partner} 的{status_text.get(r[0], r[0])}",
            "detail": f"¥{r[3]:,}" if r[3] else "",
            "time": r[2] or r[1],
            "partner": partner,
        })

    # New users on platform (public events)
    new_users = conn.execute("""
        SELECT display_name, role, created_at FROM users
        WHERE is_active = 1 AND id != ?
        ORDER BY created_at DESC LIMIT 3
    """, (user_id,)).fetchall()

    role_text = {"advertiser": "廣告主", "creator": "創作者"}
    for r in new_users:
        events.append({
            "type": "new_user",
            "icon": "🆕",
            "text": f"新{role_text.get(r[1], r[1])} {r[0]} 加入平台",
            "detail": "",
            "time": r[2],
            "partner": r[0],
        })

    # Sort all events by time descending
    events.sort(key=lambda x: x.get("time", ""), reverse=True)
    return events[:limit]
