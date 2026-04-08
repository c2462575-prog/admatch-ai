"""Simple in-memory error tracker for production observability."""
import time
import traceback
import logging
from collections import deque

logger = logging.getLogger("admatch.errors")

# Ring buffer of recent errors (last 100)
_errors: deque = deque(maxlen=100)


def track_error(source: str, error: Exception, context: dict = None):
    """Record an error for later inspection via admin API."""
    entry = {
        "time": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "timestamp": time.time(),
        "source": source,
        "error_type": type(error).__name__,
        "message": str(error),
        "traceback": traceback.format_exc(),
        "context": context or {},
    }
    _errors.append(entry)
    logger.error(f"[{source}] {type(error).__name__}: {error}")


def get_recent_errors(limit: int = 20) -> list[dict]:
    """Get most recent errors, newest first."""
    errors = list(_errors)
    errors.reverse()
    return errors[:limit]


def get_error_summary() -> dict:
    """Get error count by source."""
    summary = {}
    for e in _errors:
        src = e["source"]
        summary[src] = summary.get(src, 0) + 1
    return {
        "total_errors": len(_errors),
        "by_source": summary,
        "latest": _errors[-1] if _errors else None,
    }
