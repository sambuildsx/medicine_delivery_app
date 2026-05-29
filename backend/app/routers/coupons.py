from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from decimal import Decimal
from app.database import get_db
from app.models import Coupon, CartItem
from app.schemas import CouponApply, CouponResponse
from app.auth import get_current_user, User
from app.routers.cart import get_ist_time, to_naive_utc

router = APIRouter(prefix="/coupons", tags=["Coupons"])

@router.post("/apply", response_model=CouponResponse)
def apply_coupon(
    coupon_in: CouponApply,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Validate and apply a coupon code for the authenticated user's current cart.
    Returns the calculated discount amount and a status message.
    """
    code = coupon_in.code.strip().upper()
    
    # 1. Fetch user cart total
    cart_items = db.query(CartItem).filter(CartItem.user_id == current_user.id).all()
    if not cart_items:
        return CouponResponse(
            valid=False,
            discount_amount=Decimal("0.00"),
            message="Your cart is empty. Add medicines to apply a coupon."
        )
        
    item_total = sum(Decimal(str(item.medicine.selling_price)) * item.quantity for item in cart_items)
    
    # 2. Query the coupon database
    coupon = db.query(Coupon).filter(Coupon.code == code).first()
    if not coupon:
        return CouponResponse(
            valid=False,
            discount_amount=Decimal("0.00"),
            message=f"Coupon code '{code}' is invalid."
        )
        
    if not coupon.is_active:
        return CouponResponse(
            valid=False,
            discount_amount=Decimal("0.00"),
            message=f"Coupon code '{code}' is no longer active."
        )
        
    # 3. Check coupon expiry (IST timezone compared)
    now_ist = get_ist_time()
    if to_naive_utc(coupon.expires_at) <= to_naive_utc(now_ist):
        return CouponResponse(
            valid=False,
            discount_amount=Decimal("0.00"),
            message=f"Coupon code '{code}' has expired."
        )
        
    # 4. Check minimum cart value requirement
    min_value = Decimal(str(coupon.min_cart_value))
    if item_total < min_value:
        return CouponResponse(
            valid=False,
            discount_amount=Decimal("0.00"),
            message=f"Minimum cart value of ₹{min_value} not met. Current total is ₹{item_total}."
        )
        
    # 5. Compute the discount amount
    discount_val = Decimal(str(coupon.discount_value))
    if coupon.discount_type == "flat":
        discount_amount = min(discount_val, item_total)
    elif coupon.discount_type == "percentage":
        discount_amount = (item_total * discount_val) / Decimal("100.00")
        discount_amount = min(discount_amount, item_total)
    else:
        return CouponResponse(
            valid=False,
            discount_amount=Decimal("0.00"),
            message="Unsupported coupon discount type."
        )
        
    return CouponResponse(
        valid=True,
        discount_amount=discount_amount,
        message=f"Coupon '{code}' applied successfully! Saved ₹{discount_amount:.2f}."
    )
