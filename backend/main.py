"""
LAMYSK AURA — FastAPI Backend
Run (dev):  uvicorn backend.main:app --reload --port 8000
Run (prod): uvicorn backend.main:app --host 0.0.0.0 --port $PORT
Docs:       http://localhost:8000/docs
Admin:      http://localhost:8000/admin
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pathlib import Path

from .database import init_db
from .routers import products, orders, misc, auth, i18n, admin_upload

# ── APP SETUP ─────────────────────────────────────────────────────────────────

ENV = os.getenv("ENV", "development")

BACKEND_DIR = Path(__file__).parent
FRONTEND    = BACKEND_DIR.parent

# Persistent disk for user uploads (Render disk in prod, ./data locally).
# Fall back to a local dir if the configured DATA_DIR isn't writable —
# this keeps the app bootable even when the Render disk isn't mounted yet.
def _resolve_data_dir() -> Path:
    candidate = Path(os.getenv("DATA_DIR") or (FRONTEND / "data"))
    try:
        (candidate / "images").mkdir(parents=True, exist_ok=True)
        return candidate
    except (PermissionError, OSError) as e:
        print(f"⚠️  DATA_DIR '{candidate}' not writable ({e}); falling back to {FRONTEND/'data'}")
        fallback = FRONTEND / "data"
        (fallback / "images").mkdir(parents=True, exist_ok=True)
        return fallback

DATA_DIR = _resolve_data_dir()
UPLOAD_DIR = DATA_DIR / "images"


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Auto-seed the product catalog on first boot (empty DB). Safe on redeploy:
    # only runs when the products table is empty, so admin edits are never
    # overwritten. Manual reseed: `python -m backend.services.seed_v2`.
    await _auto_seed_if_empty()
    yield


async def _auto_seed_if_empty():
    import aiosqlite
    from .database import DB_PATH
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT COUNT(*) FROM products")
            count = (await cur.fetchone())[0]
        if count == 0:
            print("ℹ️  Products table empty — seeding catalog…")
            from .services.seed_v2 import wipe_and_seed
            await wipe_and_seed()
    except Exception as e:
        print(f"⚠️  Auto-seed skipped: {e}")


app = FastAPI(
    title="LAMYSK AURA API",
    description="Backend for the LAMYSK AURA niche fragrance store — Morocco",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs"  if ENV != "production" else None,
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

# ── ROUTERS ───────────────────────────────────────────────────────────────────

app.include_router(products.router, prefix="/api/v1")
app.include_router(orders.router,   prefix="/api/v1")
app.include_router(misc.router,     prefix="/api/v1")
app.include_router(auth.router,     prefix="/api/v1")
app.include_router(i18n.router,     prefix="/api/v1")
app.include_router(admin_upload.router, prefix="/api/v1")


# ── HEALTH CHECK ──────────────────────────────────────────────────────────────

@app.get("/api/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "LAMYSK AURA API",
        "version": "1.0.0",
        "env": ENV,
    }


# ── ADMIN DASHBOARD ───────────────────────────────────────────────────────────
# Served BEFORE the catch-all so it is not treated as a frontend route.

@app.get("/admin", include_in_schema=False)
async def serve_admin():
    return FileResponse(BACKEND_DIR / "admin.html")


# ── SERVE STATIC FRONTEND ────────────────────────────────────────────────────
# FastAPI serves index.html at / so the whole app runs from one process.

@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse(FRONTEND / "index.html")


# Catch-all for client-side routing (future multi-page expansion).
# For /images/*, prefer the persistent disk (admin uploads) then repo images.
@app.get("/{full_path:path}", include_in_schema=False)
async def serve_spa(full_path: str):
    if full_path.startswith("images/"):
        disk_path = DATA_DIR / full_path
        if disk_path.exists() and disk_path.is_file():
            return FileResponse(disk_path)
    file_path = FRONTEND / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    index = FRONTEND / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"detail": "Not found"}, 404
