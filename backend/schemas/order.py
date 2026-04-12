from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
import re


class OrderItemIn(BaseModel):
    name: str
    brand: Optional[str] = None
    size_label: Optional[str] = None
    unit_price: int = Field(..., ge=0)
    quantity: int = Field(1, ge=1, le=20)
    product_id: Optional[int] = None
    variant_id: Optional[int] = None

    @property
    def line_total(self) -> int:
        return self.unit_price * self.quantity


class OrderCreate(BaseModel):
    first_name: str = Field(..., min_length=1)
    last_name: Optional[str] = None
    phone: str = Field(..., min_length=8)
    email: Optional[str] = None
    address: str = Field(..., min_length=5)
    city: str = Field(..., min_length=2)
    zip_code: Optional[str] = None
    notes: Optional[str] = None
    delivery_method: str = Field("home", pattern="^(home|express)$")
    payment_method: str = Field("cod", pattern="^(cod|virement)$")
    lang: str = Field("fr", pattern="^(fr|ar|en)$")
    items: List[OrderItemIn] = Field(..., min_length=1)

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        cleaned = re.sub(r"[\s\-\(\)\.]+", "", v)
        if not re.match(r"^(\+212|0)(5|6|7)\d{8}$", cleaned):
            raise ValueError("Numéro de téléphone marocain invalide (ex: 06 00 00 00 00)")
        return cleaned


class OrderItemOut(BaseModel):
    id: int
    name: str
    brand: Optional[str] = None
    size_label: Optional[str] = None
    unit_price: int
    quantity: int
    line_total: int


class OrderOut(BaseModel):
    id: int
    reference: str
    first_name: str
    last_name: Optional[str] = None
    phone: str
    email: Optional[str] = None
    address: str
    city: str
    zip_code: Optional[str] = None
    notes: Optional[str] = None
    delivery_method: str
    delivery_cost: int
    payment_method: str
    subtotal: int
    total: int
    status: str
    lang: str
    created_at: str
    items: List[OrderItemOut] = []


class OrderStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|confirmed|shipped|delivered|cancelled)$")
