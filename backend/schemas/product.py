from pydantic import BaseModel, Field
from typing import Optional, List


class VariantOut(BaseModel):
    id: int
    size_label: str
    price_mad: int
    stock: int
    sku: Optional[str] = None


class ProductOut(BaseModel):
    id: int
    slug: str
    name: str
    brand: str
    category: str
    carousel_slot: Optional[str] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    badge: Optional[str] = None
    price_mad: Optional[int] = None
    sort_order: int = 0
    # i18n overrides
    brand_fr: Optional[str] = None
    brand_ar: Optional[str] = None
    brand_en: Optional[str] = None
    name_fr:  Optional[str] = None
    name_ar:  Optional[str] = None
    name_en:  Optional[str] = None
    notes_fr: Optional[str] = None
    notes_ar: Optional[str] = None
    notes_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    active: bool = True
    variants: List[VariantOut] = []


class ProductCreate(BaseModel):
    slug: str = Field(..., min_length=2)
    name: str = Field(..., min_length=1)
    brand: str = "Lamysk Aura Selection"
    category: str
    carousel_slot: Optional[str] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    badge: Optional[str] = None
    price_mad: Optional[int] = None
    sort_order: int = 0
    brand_fr: Optional[str] = None
    brand_ar: Optional[str] = None
    brand_en: Optional[str] = None
    name_fr:  Optional[str] = None
    name_ar:  Optional[str] = None
    name_en:  Optional[str] = None
    notes_fr: Optional[str] = None
    notes_ar: Optional[str] = None
    notes_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None


class VariantCreate(BaseModel):
    size_label: str
    price_mad: int = Field(..., ge=0)
    stock: int = Field(0, ge=0)
    sku: Optional[str] = None


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    brand: Optional[str] = None
    category: Optional[str] = None
    carousel_slot: Optional[str] = None
    notes: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None
    badge: Optional[str] = None
    price_mad: Optional[int] = None
    sort_order: Optional[int] = None
    brand_fr: Optional[str] = None
    brand_ar: Optional[str] = None
    brand_en: Optional[str] = None
    name_fr:  Optional[str] = None
    name_ar:  Optional[str] = None
    name_en:  Optional[str] = None
    notes_fr: Optional[str] = None
    notes_ar: Optional[str] = None
    notes_en: Optional[str] = None
    description_fr: Optional[str] = None
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    active: Optional[bool] = None
