"""
Orders router — place orders, track status, admin management.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
import aiosqlite
import string
import random

from ..database import get_db
from ..deps import require_admin
from ..routers.auth import get_optional_user
from ..schemas.order import OrderCreate, OrderOut, OrderItemOut, OrderStatusUpdate

router = APIRouter(prefix="/orders", tags=["Orders"])

DELIVERY_COSTS = {"home": 40, "express": 70}


def _generate_ref() -> str:
    chars = string.ascii_uppercase + string.digits
    return "LA-" + "".join(random.choices(chars, k=6))


async def _get_order_items(db, order_id: int) -> List[OrderItemOut]:
    cursor = await db.execute(
        "SELECT * FROM order_items WHERE order_id=?", (order_id,)
    )
    rows = await cursor.fetchall()
    return [OrderItemOut(**dict(r)) for r in rows]


async def _row_to_order(db, row) -> OrderOut:
    items = await _get_order_items(db, row["id"])
    data = dict(row)
    return OrderOut(**data, items=items)


# ── PLACE AN ORDER ────────────────────────────────────────────────────────────

@router.post("/", response_model=OrderOut, status_code=201)
async def place_order(
    order: OrderCreate,
    db: aiosqlite.Connection = Depends(get_db),
    current_user = Depends(get_optional_user),
):
    # Calculate totals
    delivery_cost = DELIVERY_COSTS.get(order.delivery_method, 40)
    subtotal = sum(item.unit_price * item.quantity for item in order.items)
    total = subtotal + delivery_cost

    # Generate unique reference
    ref = _generate_ref()
    cursor = await db.execute("SELECT id FROM orders WHERE reference=?", (ref,))
    while await cursor.fetchone():
        ref = _generate_ref()
        cursor = await db.execute("SELECT id FROM orders WHERE reference=?", (ref,))

    # Upsert customer by phone
    await db.execute(
        """INSERT INTO customers (phone, first_name, last_name, email, city)
           VALUES (?, ?, ?, ?, ?)
           ON CONFLICT(phone) DO UPDATE SET
             first_name = excluded.first_name,
             last_name  = excluded.last_name,
             city       = excluded.city""",
        (order.phone, order.first_name, order.last_name, order.email, order.city)
    )
    cursor = await db.execute("SELECT id FROM customers WHERE phone=?", (order.phone,))
    customer = await cursor.fetchone()

    user_id = current_user["id"] if current_user else None

    # Insert order
    cursor = await db.execute(
        """INSERT INTO orders
           (reference, user_id, customer_id, first_name, last_name, phone, email,
            address, city, zip_code, notes, delivery_method, delivery_cost,
            payment_method, subtotal, total, lang)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (ref, user_id, customer["id"], order.first_name, order.last_name, order.phone,
         order.email, order.address, order.city, order.zip_code, order.notes,
         order.delivery_method, delivery_cost, order.payment_method,
         subtotal, total, order.lang)
    )
    order_id = cursor.lastrowid

    # Insert items
    for item in order.items:
        await db.execute(
            """INSERT INTO order_items
               (order_id, product_id, variant_id, name, brand, size_label,
                unit_price, quantity, line_total)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (order_id, item.product_id, item.variant_id, item.name, item.brand,
             item.size_label, item.unit_price, item.quantity,
             item.unit_price * item.quantity)
        )

    await db.commit()

    cursor = await db.execute("SELECT * FROM orders WHERE id=?", (order_id,))
    row = await cursor.fetchone()
    return await _row_to_order(db, row)


# ── TRACK ORDER (public — by reference + phone) ───────────────────────────────

@router.get("/track", response_model=OrderOut)
async def track_order(
    reference: str = Query(...),
    phone: str = Query(...),
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute(
        "SELECT * FROM orders WHERE reference=? AND phone=?",
        (reference.upper(), phone)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    return await _row_to_order(db, row)


# ── ADMIN: LIST ORDERS ────────────────────────────────────────────────────────

@router.get("/", response_model=List[OrderOut], dependencies=[Depends(require_admin)])
async def list_orders(
    status: Optional[str] = None,
    city: Optional[str] = None,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: aiosqlite.Connection = Depends(get_db)
):
    where, params = [], []
    if status:
        where.append("status=?"); params.append(status)
    if city:
        where.append("city=?"); params.append(city)
    clause = ("WHERE " + " AND ".join(where)) if where else ""
    cursor = await db.execute(
        f"SELECT * FROM orders {clause} ORDER BY created_at DESC LIMIT ? OFFSET ?",
        (*params, limit, offset)
    )
    rows = await cursor.fetchall()
    return [await _row_to_order(db, r) for r in rows]


# ── ADMIN: GET ONE ORDER ──────────────────────────────────────────────────────

@router.get("/{reference}", response_model=OrderOut, dependencies=[Depends(require_admin)])
async def get_order(reference: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM orders WHERE reference=?", (reference.upper(),))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    return await _row_to_order(db, row)


# ── ADMIN: UPDATE STATUS ──────────────────────────────────────────────────────

@router.patch("/{reference}/status", response_model=OrderOut, dependencies=[Depends(require_admin)])
async def update_status(
    reference: str,
    body: OrderStatusUpdate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id FROM orders WHERE reference=?", (reference.upper(),))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    await db.execute(
        "UPDATE orders SET status=?, updated_at=datetime('now') WHERE reference=?",
        (body.status, reference.upper())
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM orders WHERE reference=?", (reference.upper(),))
    row = await cursor.fetchone()
    return await _row_to_order(db, row)


# ── ADMIN: DASHBOARD STATS ────────────────────────────────────────────────────

@router.get("/admin/stats", dependencies=[Depends(require_admin)])
async def dashboard_stats(db: aiosqlite.Connection = Depends(get_db)):
    stats = {}

    cursor = await db.execute("SELECT COUNT(*) FROM orders")
    stats["total_orders"] = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT SUM(total) FROM orders WHERE status != 'cancelled'")
    stats["total_revenue_mad"] = (await cursor.fetchone())[0] or 0

    cursor = await db.execute(
        "SELECT COUNT(*) FROM orders WHERE status='pending'"
    )
    stats["pending_orders"] = (await cursor.fetchone())[0]

    cursor = await db.execute(
        "SELECT status, COUNT(*) as cnt FROM orders GROUP BY status"
    )
    stats["by_status"] = {r["status"]: r["cnt"] for r in await cursor.fetchall()}

    cursor = await db.execute(
        "SELECT city, COUNT(*) as cnt FROM orders GROUP BY city ORDER BY cnt DESC LIMIT 10"
    )
    stats["top_cities"] = [dict(r) for r in await cursor.fetchall()]

    cursor = await db.execute(
        """SELECT oi.name, SUM(oi.quantity) as total_sold
           FROM order_items oi
           JOIN orders o ON o.id = oi.order_id
           WHERE o.status != 'cancelled'
           GROUP BY oi.name
           ORDER BY total_sold DESC
           LIMIT 10"""
    )
    stats["top_products"] = [dict(r) for r in await cursor.fetchall()]

    cursor = await db.execute(
        """SELECT date(created_at) as day, COUNT(*) as orders, SUM(total) as revenue
           FROM orders
           WHERE created_at >= date('now', '-30 days')
           GROUP BY day
           ORDER BY day"""
    )
    stats["last_30_days"] = [dict(r) for r in await cursor.fetchall()]

    # ── Cross-table counts for the overview KPI cards ─────────────────────
    cursor = await db.execute("SELECT COUNT(*) FROM customers")
    stats["total_customers"] = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM newsletter")
    stats["newsletter_subscribers"] = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM quiz_results")
    stats["quiz_submissions"] = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM contact_messages WHERE replied=0")
    stats["unreplied_messages"] = (await cursor.fetchone())[0]

    return stats
