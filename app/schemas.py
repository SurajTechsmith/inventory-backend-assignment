from pydantic import BaseModel, EmailStr, field_validator
from typing import List, Optional
from datetime import datetime


# ── Product ──────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str
    sku: str
    price: float
    quantity: int

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(cls, v):
        if v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    sku: Optional[str] = None
    price: Optional[float] = None
    quantity: Optional[int] = None

    @field_validator("price")
    @classmethod
    def price_must_be_positive(cls, v):
        if v is not None and v <= 0:
            raise ValueError("Price must be greater than 0")
        return v

    @field_validator("quantity")
    @classmethod
    def quantity_not_negative(cls, v):
        if v is not None and v < 0:
            raise ValueError("Quantity cannot be negative")
        return v


class ProductOut(BaseModel):
    id: int
    name: str
    sku: str
    price: float
    quantity: int
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Customer ─────────────────────────────────────────────
class CustomerCreate(BaseModel):
    full_name: str
    email: EmailStr
    phone: str


class CustomerOut(BaseModel):
    id: int
    full_name: str
    email: str
    phone: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Order ─────────────────────────────────────────────────
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int

    @field_validator("quantity")
    @classmethod
    def quantity_must_be_positive(cls, v):
        if v <= 0:
            raise ValueError("Order quantity must be at least 1")
        return v


class OrderItemOut(BaseModel):
    product_id: int
    quantity: int
    unit_price: float

    model_config = {"from_attributes": True}


class OrderCreate(BaseModel):
    customer_id: int
    items: List[OrderItemCreate]


class OrderOut(BaseModel):
    id: int
    customer_id: int
    total_amount: float
    created_at: datetime
    items: List[OrderItemOut]

    model_config = {"from_attributes": True}
