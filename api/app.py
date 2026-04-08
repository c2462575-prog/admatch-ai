"""FastAPI application factory."""
import time
import logging
from collections import defaultdict
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from core.config import ALLOWED_ORIGINS, DATABASE_PATH, GEMINI_API_KEY
from core.database import init_db
from api.routes import auth, advertisers, creators, matching, negotiations, pricing, stats, referrals, explore

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("admatch")


def create_app() -> FastAPI:
    init_db()
    if not GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set — AI matching and negotiation will use fallback mode.")
    else:
        logger.info("GEMINI_API_KEY configured — full AI features enabled.")

    app = FastAPI(
        title="AdMatch AI",
        description="AI-driven influencer marketing matching platform",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Simple in-memory rate limiter: 60 requests per minute per IP
    _rate_store: dict[str, list[float]] = defaultdict(list)
    RATE_LIMIT = 60
    RATE_WINDOW = 60  # seconds

    @app.middleware("http")
    async def rate_limit_and_log(request: Request, call_next):
        start = time.time()
        client_ip = request.client.host if request.client else "unknown"

        # Rate limiting (skip health checks)
        if not request.url.path.startswith("/api/health"):
            now = time.time()
            # Clean old entries
            _rate_store[client_ip] = [t for t in _rate_store[client_ip] if now - t < RATE_WINDOW]
            if len(_rate_store[client_ip]) >= RATE_LIMIT:
                return JSONResponse(status_code=429, content={"detail": "Too many requests. Please try again later."})
            _rate_store[client_ip].append(now)

        response = await call_next(request)
        duration = round((time.time() - start) * 1000)
        if not request.url.path.startswith("/api/health"):
            logger.info(f"{request.method} {request.url.path} → {response.status_code} ({duration}ms) [{client_ip}]")
        return response

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(advertisers.router, prefix="/api/advertisers", tags=["advertisers"])
    app.include_router(creators.router, prefix="/api/creators", tags=["creators"])
    app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
    app.include_router(negotiations.router, prefix="/api/negotiations", tags=["negotiations"])
    app.include_router(pricing.router, prefix="/api/pricing", tags=["pricing"])
    app.include_router(stats.router, prefix="/api/stats", tags=["stats"])
    app.include_router(referrals.router, prefix="/api/referrals", tags=["referrals"])
    app.include_router(explore.router, prefix="/api/explore", tags=["explore"])

    @app.get("/api/health")
    def health():
        """Health check with DB connectivity verification."""
        import sqlite3
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            conn.execute("SELECT 1")
            user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            conn.close()
            return {"status": "ok", "version": "1.0.0", "db": "connected", "users": user_count}
        except Exception as e:
            return {"status": "degraded", "version": "1.0.0", "db": "error", "detail": str(e)}

    return app


app = create_app()
