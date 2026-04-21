"""
Products router — CRUD for products and their size variants.
Public: GET /products, GET /products/{slug}
Admin:  POST/PATCH/DELETE (protected by X-Admin-Key header)
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
import aiosqlite

from ..database import get_db
from ..deps import require_admin
from ..schemas.product import ProductOut, ProductCreate, ProductUpdate, VariantCreate, VariantOut

router = APIRouter(prefix="/products", tags=["Products"])


# ── HELPERS ───────────────────────────────────────────────────────────────────

async def _get_variants(db: aiosqlite.Connection, product_id: int) -> list:
    cursor = await db.execute(
        "SELECT id, size_label, price_mad, stock, sku FROM product_variants WHERE product_id = ?",
        (product_id,)
    )
    rows = await cursor.fetchall()
    return [VariantOut(**dict(r)) for r in rows]


async def _row_to_product(db, row) -> ProductOut:
    variants = await _get_variants(db, row["id"])
    d = dict(row)
    d["active"] = bool(d.get("active", 1))
    d["variants"] = variants
    # Drop legacy/internal columns Pydantic doesn't need
    d.pop("created_at", None)
    return ProductOut(**d)


# ── PUBLIC ENDPOINTS ──────────────────────────────────────────────────────────

@router.get("/", response_model=List[ProductOut])
async def list_products(
    category: Optional[str] = None,
    carousel_slot: Optional[str] = None,
    include_inactive: bool = False,
    db: aiosqlite.Connection = Depends(get_db)
):
    """List products, optionally filtered by category or carousel_slot."""
    where = [] if include_inactive else ["active=1"]
    params: list = []
    if category:
        where.append("category=?"); params.append(category)
    if carousel_slot:
        where.append("carousel_slot=?"); params.append(carousel_slot)
    sql = "SELECT * FROM products"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " ORDER BY sort_order ASC, id ASC"
    cursor = await db.execute(sql, params)
    rows = await cursor.fetchall()
    return [await _row_to_product(db, r) for r in rows]


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM products WHERE slug=? AND active=1", (slug,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return await _row_to_product(db, row)


# ── ADMIN ENDPOINTS ───────────────────────────────────────────────────────────

@router.post("/", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def create_product(
    product: ProductCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    try:
        fields = product.model_dump()
        cols = ", ".join(fields.keys())
        placeholders = ", ".join(["?"] * len(fields))
        cursor = await db.execute(
            f"INSERT INTO products ({cols}) VALUES ({placeholders})",
            tuple(fields.values())
        )
        product_id = cursor.lastrowid
        await db.commit()
    except aiosqlite.IntegrityError as e:
        raise HTTPException(status_code=409, detail=f"Slug already exists: {e}")
    cursor = await db.execute("SELECT * FROM products WHERE id=?", (product_id,))
    row = await cursor.fetchone()
    return await _row_to_product(db, row)


@router.patch("/{slug}", response_model=ProductOut, dependencies=[Depends(require_admin)])
async def update_product(
    slug: str,
    update: ProductUpdate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id FROM products WHERE slug=?", (slug,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    fields = update.model_dump(exclude_none=True)
    if not fields:
        raise HTTPException(status_code=400, detail="No fields to update")
    if "active" in fields:
        fields["active"] = 1 if fields["active"] else 0
    set_clause = ", ".join(f"{k}=?" for k in fields)
    await db.execute(
        f"UPDATE products SET {set_clause} WHERE slug=?",
        (*fields.values(), slug)
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM products WHERE slug=?", (slug,))
    row = await cursor.fetchone()
    return await _row_to_product(db, row)


@router.delete("/{slug}", dependencies=[Depends(require_admin)])
async def delete_product(slug: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT id FROM products WHERE slug=?", (slug,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    await db.execute("UPDATE products SET active=0 WHERE slug=?", (slug,))
    await db.commit()
    return {"detail": f"Product '{slug}' deactivated"}


@router.post("/{slug}/variants", response_model=VariantOut, dependencies=[Depends(require_admin)])
async def add_variant(
    slug: str,
    variant: VariantCreate,
    db: aiosqlite.Connection = Depends(get_db)
):
    cursor = await db.execute("SELECT id FROM products WHERE slug=?", (slug,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    cursor = await db.execute(
        "INSERT INTO product_variants (product_id, size_label, price_mad, stock, sku) VALUES (?,?,?,?,?)",
        (row["id"], variant.size_label, variant.price_mad, variant.stock, variant.sku)
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM product_variants WHERE id=?", (cursor.lastrowid,))
    v = await cursor.fetchone()
    return VariantOut(**dict(v))


@router.patch("/variants/{variant_id}", dependencies=[Depends(require_admin)])
async def update_variant(
    variant_id: int,
    price_mad: Optional[int] = None,
    stock: Optional[int] = None,
    db: aiosqlite.Connection = Depends(get_db)
):
    updates = {}
    if price_mad is not None:
        updates["price_mad"] = price_mad
    if stock is not None:
        updates["stock"] = stock
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    set_clause = ", ".join(f"{k}=?" for k in updates)
    await db.execute(
        f"UPDATE product_variants SET {set_clause} WHERE id=?",
        (*updates.values(), variant_id)
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM product_variants WHERE id=?", (variant_id,))
    v = await cursor.fetchone()
    if not v:
        raise HTTPException(status_code=404, detail="Variant not found")
    return VariantOut(**dict(v))
