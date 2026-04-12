"""Shared FastAPI dependencies."""
import os
from fastapi import Header, HTTPException

ADMIN_KEY = os.getenv("ADMIN_KEY", "changeme-in-production")


def require_admin(x_admin_key: str = Header(None)):
    if x_admin_key != ADMIN_KEY:
        raise HTTPException(status_code=401, detail="Invalid admin key")
