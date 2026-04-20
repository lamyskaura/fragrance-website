"""
Auth router — register, login, profile, wishlist.
JWT (HS256, 30-day) + bcrypt passwords.
"""
import os
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, Depends, HTTPException, Header
from jose import jwt, JWTError
import aiosqlite

from ..database import get_db
from ..schemas.auth import UserRegister, UserLogin, UserProfileUpdate

router = APIRouter(prefix="/auth", tags=["Auth"])

SECRET_KEY   = os.getenv("SECRET_KEY", "dev-secret-please-change-in-production")
ALGORITHM    = "HS256"
EXPIRE_DAYS  = 30


def _hash_pw(password: str) -> str:
    # bcrypt hard-limits secrets to 72 bytes; truncate defensively.
    raw = password.encode("utf-8")[:72]
    return bcrypt.hashpw(raw, bcrypt.gensalt()).decode("utf-8")


def _verify_pw(password: str, hashed: str) -> bool:
    raw = password.encode("utf-8")[:72]
    try:
        return bcrypt.checkpw(raw, hashed.encode("utf-8"))
    except ValueError:
        return False


# ── TOKEN HELPERS ─────────────────────────────────────────────────

def _make_token(user_id: int) -> str:
    exp = datetime.now(timezone.utc) + timedelta(days=EXPIRE_DAYS)
    return jwt.encode({"sub": str(user_id), "exp": exp}, SECRET_KEY, algorithm=ALGORITHM)


def _decode_token(token: str) -> Optional[int]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        return None


# ── AUTH DEPENDENCY ───────────────────────────────────────────────

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: aiosqlite.Connection = Depends(get_db),
):
    """Dependency: returns current user row or raises 401."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    user_id = _decode_token(authorization[7:])
    if not user_id:
        raise HTTPException(status_code=401, detail="Token invalide ou expiré")
    cursor = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = await cursor.fetchone()
    if not user:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable")
    return user


async def get_optional_user(
    authorization: Optional[str] = Header(None),
    db: aiosqlite.Connection = Depends(get_db),
):
    """Dependency: returns user row if a valid token is present, else None."""
    if not authorization or not authorization.startswith("Bearer "):
        return None
    user_id = _decode_token(authorization[7:])
    if not user_id:
        return None
    cursor = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    return await cursor.fetchone()


def _safe(row) -> dict:
    """Return user dict without password_hash."""
    d = dict(row)
    d.pop("password_hash", None)
    return d


# ── REGISTER ──────────────────────────────────────────────────────

@router.post("/register", status_code=201)
async def register(body: UserRegister, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT id FROM users WHERE email=?", (body.email,))
    if await cursor.fetchone():
        raise HTTPException(status_code=409, detail="Cet email est déjà utilisé")

    pw_hash = _hash_pw(body.password)
    cursor = await db.execute(
        """INSERT INTO users (email, password_hash, first_name, last_name, phone, lang)
           VALUES (?,?,?,?,?,?)""",
        (body.email, pw_hash, body.first_name, body.last_name, body.phone, body.lang),
    )
    await db.commit()
    user_id = cursor.lastrowid
    token = _make_token(user_id)

    cursor = await db.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = _safe(await cursor.fetchone())
    return {"access_token": token, "token_type": "bearer", "user": user}


# ── LOGIN ─────────────────────────────────────────────────────────

@router.post("/login")
async def login(body: UserLogin, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM users WHERE email=?", (body.email,))
    row = await cursor.fetchone()
    if not row or not _verify_pw(body.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Email ou mot de passe incorrect")

    token = _make_token(row["id"])
    return {"access_token": token, "token_type": "bearer", "user": _safe(row)}


# ── ME ────────────────────────────────────────────────────────────

@router.get("/me")
async def me(current_user=Depends(get_current_user)):
    return _safe(current_user)


@router.patch("/me")
async def update_profile(
    body: UserProfileUpdate,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    updates = {k: v for k, v in body.model_dump().items() if v is not None}
    if not updates:
        raise HTTPException(status_code=400, detail="Aucun champ à mettre à jour")
    set_clause = ", ".join(f"{k}=?" for k in updates)
    await db.execute(
        f"UPDATE users SET {set_clause}, updated_at=datetime('now') WHERE id=?",
        (*updates.values(), current_user["id"]),
    )
    await db.commit()
    cursor = await db.execute("SELECT * FROM users WHERE id=?", (current_user["id"],))
    return _safe(await cursor.fetchone())


# ── WISHLIST ──────────────────────────────────────────────────────

@router.get("/wishlist")
async def get_wishlist(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    cursor = await db.execute(
        "SELECT product_name, added_at FROM user_wishlists WHERE user_id=? ORDER BY added_at DESC",
        (current_user["id"],),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.post("/wishlist/{product_name}", status_code=201)
async def add_to_wishlist(
    product_name: str,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    try:
        await db.execute(
            "INSERT INTO user_wishlists (user_id, product_name) VALUES (?,?)",
            (current_user["id"], product_name),
        )
        await db.commit()
    except Exception:
        pass  # already in wishlist
    return {"detail": "Added"}


@router.delete("/wishlist/{product_name}")
async def remove_from_wishlist(
    product_name: str,
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    await db.execute(
        "DELETE FROM user_wishlists WHERE user_id=? AND product_name=?",
        (current_user["id"], product_name),
    )
    await db.commit()
    return {"detail": "Removed"}


# ── USER ORDERS ───────────────────────────────────────────────────

@router.get("/orders")
async def my_orders(
    current_user=Depends(get_current_user),
    db: aiosqlite.Connection = Depends(get_db),
):
    cursor = await db.execute(
        "SELECT * FROM orders WHERE user_id=? ORDER BY created_at DESC",
        (current_user["id"],),
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]
