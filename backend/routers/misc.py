"""
Miscellaneous routes: newsletter, quiz results, contact messages.
"""
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List
import aiosqlite
import os

from ..database import get_db
from ..schemas.misc import (
    NewsletterSubscribe, QuizResultCreate,
    ContactMessageCreate, MessageOut
)

router = APIRouter(tags=["Misc"])

ADMIN_KEY = os.getenv("ADMIN_KEY", "changeme-in-production")


def require_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")


# ── NEWSLETTER ────────────────────────────────────────────────────────────────

@router.post("/newsletter", response_model=MessageOut, status_code=201)
async def subscribe(body: NewsletterSubscribe, db: aiosqlite.Connection = Depends(get_db)):
    try:
        await db.execute(
            "INSERT INTO newsletter (email, lang) VALUES (?, ?)",
            (body.email.lower().strip(), body.lang)
        )
        await db.commit()
    except aiosqlite.IntegrityError:
        return MessageOut(detail="Already subscribed")
    return MessageOut(detail="Subscribed successfully")


@router.get("/newsletter", dependencies=[Depends(require_admin)])
async def list_subscribers(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT email, lang, created_at FROM newsletter ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


# ── QUIZ RESULTS ──────────────────────────────────────────────────────────────

@router.post("/quiz", response_model=MessageOut, status_code=201)
async def save_quiz(body: QuizResultCreate, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute(
        "INSERT INTO quiz_results (profile, promo_code, phone, email, lang) VALUES (?,?,?,?,?)",
        (body.profile, body.promo_code, body.phone, body.email, body.lang)
    )
    await db.commit()
    return MessageOut(detail="Quiz result saved")


@router.get("/quiz", dependencies=[Depends(require_admin)])
async def list_quiz_results(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "SELECT profile, promo_code, phone, email, lang, created_at FROM quiz_results ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.get("/quiz/stats", dependencies=[Depends(require_admin)])
async def quiz_stats(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "SELECT profile, COUNT(*) as count FROM quiz_results GROUP BY profile ORDER BY count DESC"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


# ── CONTACT MESSAGES ──────────────────────────────────────────────────────────

@router.post("/contact", response_model=MessageOut, status_code=201)
async def send_message(body: ContactMessageCreate, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute(
        "INSERT INTO contact_messages (name, phone, message) VALUES (?,?,?)",
        (body.name, body.phone, body.message)
    )
    await db.commit()
    return MessageOut(detail="Message sent")


@router.get("/contact", dependencies=[Depends(require_admin)])
async def list_messages(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "SELECT * FROM contact_messages ORDER BY created_at DESC"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.patch("/contact/{msg_id}/replied", dependencies=[Depends(require_admin)])
async def mark_replied(msg_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("UPDATE contact_messages SET replied=1 WHERE id=?", (msg_id,))
    await db.commit()
    return {"detail": "Marked as replied"}
