"""FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.config import ALLOWED_ORIGINS
from core.database import init_db
from api.routes import auth, advertisers, creators, matching, negotiations, pricing


def create_app() -> FastAPI:
    init_db()

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

    app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
    app.include_router(advertisers.router, prefix="/api/advertisers", tags=["advertisers"])
    app.include_router(creators.router, prefix="/api/creators", tags=["creators"])
    app.include_router(matching.router, prefix="/api/matching", tags=["matching"])
    app.include_router(negotiations.router, prefix="/api/negotiations", tags=["negotiations"])
    app.include_router(pricing.router, prefix="/api/pricing", tags=["pricing"])

    @app.get("/api/health")
    def health():
        return {"status": "ok", "version": "1.0.0"}

    return app


app = create_app()
