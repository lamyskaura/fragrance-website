"""
SQLite database connection and initialization using aiosqlite.
All tables are created on startup if they don't exist.
"""
import aiosqlite
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

def _resolve_db_path() -> Path:
    """
    Resolve the database path:
      • If DATA_DIR is set and writable → <DATA_DIR>/lamyskaura.db (persistent disk on Render).
      • In production, a set-but-unwritable DATA_DIR is fatal — we refuse to
        fall back silently to ephemeral storage (that's how accounts get wiped
        on redeploy).
      • In dev (ENV!=production), fall back to <repo>/data/ for convenience.
    """
    env = os.getenv("ENV", "development")
    candidate = os.environ.get("DATA_DIR")

    if candidate:
        p = Path(candidate)
        try:
            p.mkdir(parents=True, exist_ok=True)
            probe = p / ".write_probe"
            probe.touch()
            probe.unlink()
            return p / "lamyskaura.db"
        except (PermissionError, OSError) as e:
            if env == "production":
                raise RuntimeError(
                    f"DATA_DIR='{candidate}' is not writable ({e}). "
                    f"Refusing to fall back to ephemeral storage in production. "
                    f"Check that the Render persistent disk is attached and mounted at this path."
                ) from e
            print(f"⚠️  DATA_DIR '{candidate}' not writable ({e}); dev fallback → ./data/")

    default = Path(__file__).parent.parent / "data"
    default.mkdir(parents=True, exist_ok=True)
    return default / "lamyskaura.db"


DB_PATH = _resolve_db_path()
print(f"📂 DB_PATH resolved → {DB_PATH} (exists={DB_PATH.exists()}, DATA_DIR={os.getenv('DATA_DIR')!r})")


async def get_db() -> aiosqlite.Connection:
    """Dependency: yields an aiosqlite connection with row_factory set."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("PRAGMA foreign_keys=ON")
        yield db


async def init_db():
    """Create all tables on application startup."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        await db.execute("PRAGMA foreign_keys=ON")

        # ── PRODUCTS ──────────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                slug           TEXT    NOT NULL UNIQUE,
                name           TEXT    NOT NULL,
                brand          TEXT    NOT NULL DEFAULT 'Lamysk Aura Selection',
                category       TEXT    NOT NULL,           -- orient | occident | absolus | ecrins | essentiels
                carousel_slot  TEXT,                       -- match | arabian_oud | ghawali | lattafa | niche | absolus | essentiels
                notes          TEXT,
                description    TEXT,
                head_notes     TEXT,
                heart_notes    TEXT,
                base_notes     TEXT,
                image_url      TEXT,
                badge          TEXT,
                price_mad      INTEGER,                    -- display price shown on the card (primary variant)
                discount_pct   INTEGER NOT NULL DEFAULT 0, -- 0–99; final price = price_mad * (1 - pct/100)
                sort_order     INTEGER NOT NULL DEFAULT 0,
                -- i18n overrides (nullable; fallback to the language-neutral column above)
                brand_fr       TEXT,  brand_ar       TEXT,  brand_en       TEXT,
                name_fr        TEXT,  name_ar        TEXT,  name_en        TEXT,
                notes_fr       TEXT,  notes_ar       TEXT,  notes_en       TEXT,
                description_fr TEXT,  description_ar TEXT,  description_en TEXT,
                active         INTEGER NOT NULL DEFAULT 1,
                created_at     TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── PRODUCT VARIANTS (sizes / versions) ───────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS product_variants (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id  INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
                size_label  TEXT    NOT NULL,           -- e.g. '50ml', '100ml', 'Coffret'
                price_mad   INTEGER NOT NULL,           -- price in MAD (integer, no decimals)
                stock       INTEGER NOT NULL DEFAULT 0,
                sku         TEXT    UNIQUE
            )
        """)

        # ── USERS (registered accounts) ───────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                email         TEXT    NOT NULL UNIQUE,
                password_hash TEXT    NOT NULL,
                first_name    TEXT    NOT NULL,
                last_name     TEXT,
                phone         TEXT,
                city          TEXT,
                lang          TEXT    NOT NULL DEFAULT 'fr',
                created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── USER WISHLISTS ─────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS user_wishlists (
                id           INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id      INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                product_name TEXT    NOT NULL,
                added_at     TEXT    NOT NULL DEFAULT (datetime('now')),
                UNIQUE(user_id, product_name)
            )
        """)

        # ── CUSTOMERS ─────────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                phone      TEXT    NOT NULL UNIQUE,
                first_name TEXT,
                last_name  TEXT,
                email      TEXT,
                city       TEXT,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── NEWSLETTER SUBSCRIBERS ────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS newsletter (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                email      TEXT    NOT NULL UNIQUE,
                lang       TEXT    NOT NULL DEFAULT 'fr',
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── ORDERS ────────────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                reference       TEXT    NOT NULL UNIQUE,   -- e.g. LA-XYZ123
                user_id         INTEGER REFERENCES users(id),
                customer_id     INTEGER REFERENCES customers(id),
                first_name      TEXT    NOT NULL,
                last_name       TEXT,
                phone           TEXT    NOT NULL,
                email           TEXT,
                address         TEXT    NOT NULL,
                city            TEXT    NOT NULL,
                zip_code        TEXT,
                notes           TEXT,
                delivery_method TEXT    NOT NULL DEFAULT 'home',   -- home | express
                delivery_cost   INTEGER NOT NULL DEFAULT 40,
                payment_method  TEXT    NOT NULL DEFAULT 'cod',    -- cod | virement
                subtotal        INTEGER NOT NULL DEFAULT 0,
                total           INTEGER NOT NULL DEFAULT 0,
                status          TEXT    NOT NULL DEFAULT 'pending', -- pending | confirmed | shipped | delivered | cancelled
                lang            TEXT    NOT NULL DEFAULT 'fr',
                created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
                updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── ORDER ITEMS ───────────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id    INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
                product_id  INTEGER REFERENCES products(id),
                variant_id  INTEGER REFERENCES product_variants(id),
                name        TEXT    NOT NULL,
                brand       TEXT,
                size_label  TEXT,
                unit_price  INTEGER NOT NULL,
                quantity    INTEGER NOT NULL DEFAULT 1,
                line_total  INTEGER NOT NULL
            )
        """)

        # ── QUIZ RESULTS (lead capture) ───────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS quiz_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                profile     TEXT    NOT NULL,            -- woody | floral | spicy | citrus | soft
                promo_code  TEXT    NOT NULL,
                phone       TEXT,
                email       TEXT,
                lang        TEXT    NOT NULL DEFAULT 'fr',
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── CONTACT MESSAGES ──────────────────────────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS contact_messages (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT,
                phone      TEXT,
                message    TEXT    NOT NULL,
                replied    INTEGER NOT NULL DEFAULT 0,
                created_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── UI STRINGS (i18n, editable from admin) ────────────────
        await db.execute("""
            CREATE TABLE IF NOT EXISTS ui_strings (
                key        TEXT    PRIMARY KEY,
                fr         TEXT,
                ar         TEXT,
                en         TEXT,
                group_name TEXT,                                  -- nav | hero | quiz | footer | checkout | ...
                updated_at TEXT    NOT NULL DEFAULT (datetime('now'))
            )
        """)

        # ── MIGRATIONS ────────────────────────────────────────────
        # Older DBs may miss user_id on orders — add it if absent.
        cur = await db.execute("PRAGMA table_info(orders)")
        cols = {r["name"] for r in await cur.fetchall()}
        if "user_id" not in cols:
            await db.execute("ALTER TABLE orders ADD COLUMN user_id INTEGER REFERENCES users(id)")

        # Older DBs may miss the new product columns — add each if absent.
        cur = await db.execute("PRAGMA table_info(products)")
        pcols = {r["name"] for r in await cur.fetchall()}
        new_product_cols = [
            ("carousel_slot",  "TEXT"),
            ("price_mad",      "INTEGER"),
            ("discount_pct",   "INTEGER NOT NULL DEFAULT 0"),
            ("sort_order",     "INTEGER NOT NULL DEFAULT 0"),
            ("head_notes",     "TEXT"),
            ("heart_notes",    "TEXT"),
            ("base_notes",     "TEXT"),
            ("brand_fr",       "TEXT"), ("brand_ar",       "TEXT"), ("brand_en",       "TEXT"),
            ("name_fr",        "TEXT"), ("name_ar",        "TEXT"), ("name_en",        "TEXT"),
            ("notes_fr",       "TEXT"), ("notes_ar",       "TEXT"), ("notes_en",       "TEXT"),
            ("description_fr", "TEXT"), ("description_ar", "TEXT"), ("description_en", "TEXT"),
        ]
        for col, coltype in new_product_cols:
            if col not in pcols:
                await db.execute(f"ALTER TABLE products ADD COLUMN {col} {coltype}")

        await db.commit()
        print(f"✅ Database initialized at {DB_PATH}")
