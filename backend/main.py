"""
LAMYSK AURA — FastAPI Backend
Run (dev):  uvicorn backend.main:app --reload --port 8000
Run (prod): uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Docs:       http://localhost:8000/docs
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from .database import init_db
from .routers import products, orders, misc

# ── APP SETUP ─────────────────────────────────────────────────────────────────

ENV = os.getenv("ENV", "development")

app = FastAPI(
    title="LAMYSK AURA API",
    description="Backend for the LAMYSK AURA niche fragrance store — Morocco",
    version="1.0.0",
    # Hide docs in production
    docs_url="/docs" if ENV != "production" else None,
    redoc_url="/redoc" if ENV != "production" else None,
)

# Allow all origins in dev; tighten to your domain in production
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DATABASE INIT ON STARTUP ──────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    await init_db()
    from .services.seed import seed
    await seed()


# ── ROUTERS ───────────────────────────────────────────────────────────────────

app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router,   prefix="/api/v1")
app.include_router(misc.router,     prefix="/api/v1")


# ── SERVE STATIC FRONTEND ────────────────────────────────────────────────────
# FastAPI serves index.html at / so the whole app runs from one process.

FRONTEND = Path(__file__).parent.parent

@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(FRONTEND / "index.html")

# Catch-all for client-side routing (future multi-page expansion)
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    # Always return index.html for unknown paths (SPA fallback)
    index = FRONTEND / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"detail": "Not found"}, 404


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "LAMYSK AURA API",
        "version": "1.0.0",
        "env": ENV,
    }
