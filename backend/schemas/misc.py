from pydantic import BaseModel, Field, EmailStr
from typing import Optional


class NewsletterSubscribe(BaseModel):
    email: str = Field(..., min_length=5)
    lang: str = Field("fr", pattern="^(fr|ar|en)$")


class QuizResultCreate(BaseModel):
    profile: str = Field(..., pattern="^(woody|floral|spicy|citrus|soft)$")
    promo_code: str
    phone: Optional[str] = None
    email: Optional[str] = None
    lang: str = Field("fr", pattern="^(fr|ar|en)$")


class ContactMessageCreate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    message: str = Field(..., min_length=5)


class MessageOut(BaseModel):
    detail: str
