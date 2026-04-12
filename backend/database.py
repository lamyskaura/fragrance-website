"""
SQLite database connection and initialization using aiosqlite.
All tables are created on startup if they don't exist.
"""
import aiosqlite
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# On cloud platforms (Render, Railway) with a mounted disk, set DATA_DIR env var.
# Falls back to a local ./data/ directory for development.
_data_dir = os.environ.get("DATA_DIR") or str(Path(__file__).parent.parent / "data")
DB_PATH = Path(_data_dir) / "lamyskaura.db"


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
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                slug        TEXT    NOT NULL UNIQUE,
                name        TEXT    NOT NULL,
                brand       TEXT    NOT NULL DEFAULT 'Lamysk Aura Selection',
                category    TEXT    NOT NULL,           -- orient | occident | absolus | ecrins | essentiels
                notes       TEXT,
                description TEXT,
                image_url   TEXT,
                badge       TEXT,
                active      INTEGER NOT NULL DEFAULT 1,
                created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
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

        await db.commit()
        print(f"✅ Database initialized at {DB_PATH}")
