"""
Admin-only product image upload.

Images land on the persistent disk ($DATA_DIR/images/) and the returned URL
('images/<filename>') is stored verbatim in products.image_url. Serving is
handled by the catch-all in main.py, which checks the disk before the repo.
"""
import os
import re
import secrets
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form

from ..deps import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"], dependencies=[Depends(require_admin)])

_PROJECT_ROOT = Path(__file__).parent.parent.parent


def _resolve_upload_dir() -> Path:
    candidate = Path(os.getenv("DATA_DIR") or (_PROJECT_ROOT / "data")) / "images"
    try:
        candidate.mkdir(parents=True, exist_ok=True)
        return candidate
    except (PermissionError, OSError):
        fallback = _PROJECT_ROOT / "data" / "images"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


UPLOAD_DIR = _resolve_upload_dir()

ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp"}
EXT_BY_MIME = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}
MAX_BYTES = 5 * 1024 * 1024  # 5 MB


def _slugify(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return s[:40] or "image"


@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    slug: str = Form(""),
):
    if file.content_type not in ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Format non supporté (JPG, PNG, WEBP uniquement)")

    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(status_code=413, detail="Image trop lourde (max 5 Mo)")
    if not data:
        raise HTTPException(status_code=400, detail="Fichier vide")

    ext = EXT_BY_MIME[file.content_type]
    stem = _slugify(slug) if slug else _slugify(Path(file.filename or "img").stem)
    filename = f"{stem}-{secrets.token_hex(4)}{ext}"
    dest = UPLOAD_DIR / filename
    dest.write_bytes(data)

    return {"url": f"images/{filename}", "filename": filename, "size": len(data)}
