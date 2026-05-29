from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

# --- AUTH SCHEMAS ---

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password must be at least 6 characters")
    full_name: str = Field(..., min_length=2, description="Name must be at least 2 characters")

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: str
    full_name: str

class UserOut(BaseModel):
    id: int
    email: str
    full_name: str
    
    model_config = ConfigDict(from_attributes=True)


# --- MEDICINE SCHEMAS ---

class MedicineOut(BaseModel):
    id: int
    name: str
    salt_composition: str
    mrp: Decimal
    selling_price: Decimal
    stock: int
    prescription_required: bool
    
    model_config = ConfigDict(from_attributes=True)


# --- CART SCHEMAS ---

class CartItemAdd(BaseModel):
    medicine_id: int
    quantity: int = Field(1, ge=1)

class CartItemUpdate(BaseModel):
    quantity: int = Field(..., ge=1)

class CartItemOut(BaseModel):
    id: int
    medicine_id: int
    quantity: int
    medicine: MedicineOut
    
    model_config = ConfigDict(from_attributes=True)

class CartOut(BaseModel):
    items: List[CartItemOut]
    item_total: Decimal
    discount_amount: Decimal
    small_cart_fee: Decimal
    delivery_fee: Decimal
    late_night_fee: Decimal
    total_payable: Decimal
    coupon_applied: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


# --- SERVICEABILITY SCHEMAS ---

class ServiceabilityCheck(BaseModel):
    pincode: str = Field(..., min_length=4, max_length=10)
    distance: int = Field(..., ge=0, description="Distance from store in meters")

class ServiceabilityResponse(BaseModel):
    serviceable: bool
    distance: int
    estimated_delivery_minutes: Optional[int] = None
    message: str


# --- ORDER SCHEMAS ---

class OrderPlace(BaseModel):
    pincode: str = Field(..., min_length=4, max_length=10)
    distance: int = Field(..., ge=0)
    coupon_code: Optional[str] = None

class OrderItemOut(BaseModel):
    id: int
    medicine_id: Optional[int] = None
    quantity: int
    name: str
    salt_composition: str
    selling_price: Decimal
    
    model_config = ConfigDict(from_attributes=True)

class OrderOut(BaseModel):
    id: int
    user_id: int
    status: str
    pincode: str
    distance: int
    estimated_delivery_minutes: int
    item_total: Decimal
    discount_amount: Decimal
    small_cart_fee: Decimal
    delivery_fee: Decimal
    late_night_fee: Decimal
    total_payable: Decimal
    coupon_applied: Optional[str] = None
    created_at: datetime
    items: List[OrderItemOut]
    
    model_config = ConfigDict(from_attributes=True)


# --- COUPON SCHEMAS ---

class CouponApply(BaseModel):
    code: str

class CouponResponse(BaseModel):
    valid: bool
    discount_amount: Decimal
    message: str
