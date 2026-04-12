"""
LAMYSK AURA — FastAPI Backend
Run:  uvicorn backend.main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from .database import init_db
from .routers import products, orders, misc

# ── APP SETUP ─────────────────────────────────────────────────────────────────

app = FastAPI(
    title="LAMYSK AURA API",
    description="Backend for the LAMYSK AURA niche fragrance store — Morocco",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── DATABASE INIT ON STARTUP ──────────────────────────────────────────────────

@app.on_event("startup")
async def on_startup():
    await init_db()
    # Auto-seed catalogue if the DB is empty
    from .services.seed import seed
    await seed()


# ── ROUTERS ───────────────────────────────────────────────────────────────────

app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router,   prefix="/api/v1")
app.include_router(misc.router,     prefix="/api/v1")


# ── SERVE STATIC FRONTEND ─────────────────────────────────────────────────────

FRONTEND = Path(__file__).parent.parent

@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(FRONTEND / "index.html")


# ── HEALTH CHECK ─────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
async def health():
    return {"status": "ok", "service": "LAMYSK AURA API", "version": "1.0.0"}
