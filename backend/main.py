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
# In production we refuse to fall back to ephemeral storage — silently writing
# to the project dir is what wipes uploads/accounts on every redeploy.
def _resolve_data_dir() -> Path:
    candidate = Path(os.getenv("DATA_DIR") or (FRONTEND / "data"))
    try:
        (candidate / "images").mkdir(parents=True, exist_ok=True)
        return candidate
    except (PermissionError, OSError) as e:
        if ENV == "production":
            raise RuntimeError(
                f"DATA_DIR '{candidate}' not writable ({e}). "
                f"Refusing ephemeral fallback in production — check the Render disk mount."
            ) from e
        print(f"⚠️  DATA_DIR '{candidate}' not writable ({e}); dev fallback → {FRONTEND/'data'}")
        fallback = FRONTEND / "data"
        (fallback / "images").mkdir(parents=True, exist_ok=True)
        return fallback

DATA_DIR = _resolve_data_dir()
UPLOAD_DIR = DATA_DIR / "images"
print(f"📂 DATA_DIR={DATA_DIR}  UPLOAD_DIR={UPLOAD_DIR}  ENV={ENV}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Auto-seed the product catalog on first boot (empty DB). Safe on redeploy:
    # only runs when the products table is empty, so admin edits are never
    # overwritten. Manual reseed: `python -m backend.services.seed_v2`.
    await _auto_seed_if_empty()
    # Insert any catalog slugs missing from the DB. Idempotent — existing
    # products (with potential admin edits) are never touched.
    await _sync_missing_catalog_slugs()
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


async def _sync_missing_catalog_slugs():
    """Insert catalog slugs absent from the DB without touching existing rows."""
    import aiosqlite
    from .database import DB_PATH
    from .services.seed_v2 import PRODUCTS
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cur = await db.execute("SELECT slug FROM products")
            existing = {r[0] for r in await cur.fetchall()}
            cur = await db.execute("SELECT COALESCE(MAX(sort_order), -1) FROM products")
            next_order = (await cur.fetchone())[0] + 1
            missing = [p for p in PRODUCTS if p["slug"] not in existing]
            if not missing:
                return
            for p in missing:
                await db.execute("""
                    INSERT INTO products (
                        slug, name, brand, category, carousel_slot,
                        notes, image_url, badge, price_mad, sort_order,
                        brand_fr, brand_ar, brand_en,
                        name_fr,  name_ar,  name_en,
                        notes_fr, notes_ar, notes_en,
                        active
                    ) VALUES (
                        :slug, :name, :brand, :category, :carousel_slot,
                        :notes, :image_url, :badge, :price_mad, :sort_order,
                        :brand_fr, :brand_ar, :brand_en,
                        :name_fr,  :name_ar,  :name_en,
                        :notes_fr, :notes_ar, :notes_en,
                        1
                    )
                """, {
                    "slug": p["slug"],
                    "name": p["fr"]["name"],
                    "brand": p["fr"]["brand"],
                    "category": p["category"],
                    "carousel_slot": p["carousel_slot"],
                    "notes": p["fr"]["notes"],
                    "image_url": p.get("image_url"),
                    "badge": p.get("badge"),
                    "price_mad": p["price_mad"],
                    "sort_order": next_order,
                    "brand_fr": p["fr"]["brand"], "brand_ar": p["ar"]["brand"], "brand_en": p["en"]["brand"],
                    "name_fr":  p["fr"]["name"],  "name_ar":  p["ar"]["name"],  "name_en":  p["en"]["name"],
                    "notes_fr": p["fr"]["notes"], "notes_ar": p["ar"]["notes"], "notes_en": p["en"]["notes"],
                })
                next_order += 1
            await db.commit()
            print(f"ℹ️  Synced {len(missing)} missing catalog slug(s): {', '.join(p['slug'] for p in missing)}")
    except Exception as e:
        print(f"⚠️  Slug sync skipped: {e}")


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
