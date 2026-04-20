"""
i18n router — public GET /i18n returns all UI strings grouped by language.
Admin PUT /i18n/{key} upserts a single key.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import aiosqlite

from ..database import get_db
from ..deps import require_admin

router = APIRouter(prefix="/i18n", tags=["i18n"])


class UiString(BaseModel):
    key: str
    fr: Optional[str] = None
    ar: Optional[str] = None
    en: Optional[str] = None
    group_name: Optional[str] = None


@router.get("/")
async def get_all_strings(db: aiosqlite.Connection = Depends(get_db)):
    """
    Returns { fr: {key: value, ...}, ar: {...}, en: {...}, _meta: {groups: {...}} }
    The frontend loads this once at boot and caches it.
    """
    cursor = await db.execute("SELECT key, fr, ar, en, group_name FROM ui_strings")
    rows = await cursor.fetchall()
    out: dict = {"fr": {}, "ar": {}, "en": {}, "_meta": {"groups": {}}}
    for r in rows:
        out["fr"][r["key"]] = r["fr"] or ""
        out["ar"][r["key"]] = r["ar"] or ""
        out["en"][r["key"]] = r["en"] or ""
        if r["group_name"]:
            out["_meta"]["groups"].setdefault(r["group_name"], []).append(r["key"])
    return out


@router.get("/admin", dependencies=[Depends(require_admin)])
async def list_strings_admin(db: aiosqlite.Connection = Depends(get_db)):
    """Flat list for admin editing."""
    cursor = await db.execute(
        "SELECT key, fr, ar, en, group_name, updated_at FROM ui_strings ORDER BY group_name, key"
    )
    rows = await cursor.fetchall()
    return [dict(r) for r in rows]


@router.put("/{key}", dependencies=[Depends(require_admin)])
async def upsert_string(
    key: str, body: UiString, db: aiosqlite.Connection = Depends(get_db)
):
    await db.execute("""
        INSERT INTO ui_strings (key, fr, ar, en, group_name)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(key) DO UPDATE SET
            fr=excluded.fr, ar=excluded.ar, en=excluded.en,
            group_name=excluded.group_name,
            updated_at=datetime('now')
    """, (key, body.fr, body.ar, body.en, body.group_name))
    await db.commit()
    return {"detail": "ok", "key": key}


@router.delete("/{key}", dependencies=[Depends(require_admin)])
async def delete_string(key: str, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("DELETE FROM ui_strings WHERE key=?", (key,))
    await db.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"detail": "deleted", "key": key}
