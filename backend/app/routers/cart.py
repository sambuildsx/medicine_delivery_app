from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models import CartItem, Medicine, Coupon
from app.schemas import CartItemAdd, CartItemUpdate, CartItemOut, CartOut
from app.auth import get_current_user, User

router = APIRouter(prefix="/cart", tags=["Cart"])

# --- IST Time Helpers ---

def get_ist_time() -> datetime:
    """Get the current time in Indian Standard Time (IST)."""
    utc_now = datetime.now(timezone.utc)
    ist_tz = timezone(timedelta(hours=5, minutes=30))
    return utc_now.astimezone(ist_tz)

def to_naive_utc(dt: datetime) -> datetime:
    """Convert any datetime (aware or naive) to a naive UTC datetime for database comparisons."""
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt

def is_late_night() -> bool:
    """Check if the current IST time is between 10 PM and 6 AM."""
    ist_time = get_ist_time()
    hour = ist_time.hour
    return hour >= 22 or hour < 6


# --- Dynamic Fee Calculations ---

def calculate_cart_details(cart_items: list, distance: int = 0, coupon_code: Optional[str] = None, db: Session = None):
    """Calculates all totals, discounts, and fees based on the business rules."""
    item_total = sum(Decimal(str(item.medicine.selling_price)) * item.quantity for item in cart_items)
    
    # Calculate Coupon Discount
    discount_amount = Decimal("0.00")
    applied_coupon = None
    
    if coupon_code and db and item_total > 0:
        coupon = db.query(Coupon).filter(
            Coupon.code == coupon_code.strip().upper(),
            Coupon.is_active == True
        ).first()
        
        if coupon:
            now_ist = get_ist_time()
            if to_naive_utc(coupon.expires_at) > to_naive_utc(now_ist) and item_total >= Decimal(str(coupon.min_cart_value)):
                if coupon.discount_type == "flat":
                    discount_amount = min(Decimal(str(coupon.discount_value)), item_total)
                elif coupon.discount_type == "percentage":
                    discount_amount = (item_total * Decimal(str(coupon.discount_value))) / Decimal("100.00")
                    discount_amount = min(discount_amount, item_total)
                applied_coupon = coupon.code

                
    # Discounted total for checking small cart fee
    discounted_total = item_total - discount_amount
    
    # Small Cart Fee: Item total (after discount) < Rs 199
    small_cart_fee = Decimal("0.00")
    if len(cart_items) > 0 and discounted_total < Decimal("199.00"):
        small_cart_fee = Decimal("29.00")
        
    # Delivery Fee: Distance > 2000m
    delivery_fee = Decimal("0.00")
    if distance > 2000:
        delivery_fee = Decimal("40.00")
        
    # Late Night Fee: Order between 10 PM and 6 AM IST
    late_night_fee = Decimal("0.00")
    if len(cart_items) > 0 and is_late_night():
        late_night_fee = Decimal("25.00")
        
    total_payable = discounted_total + small_cart_fee + delivery_fee + late_night_fee
    
    return {
        "item_total": item_total,
        "discount_amount": discount_amount,
        "small_cart_fee": small_cart_fee,
        "delivery_fee": delivery_fee,
        "late_night_fee": late_night_fee,
        "total_payable": total_payable,
        "coupon_applied": applied_coupon
    }


# --- API Routes ---

@router.post("/items", response_model=CartItemOut, status_code=status.HTTP_201_CREATED)
def add_to_cart(
    item_in: CartItemAdd,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a medicine to the user's cart or increment its quantity if already present."""
    medicine = db.query(Medicine).filter(Medicine.id == item_in.medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine not found")
        
    if medicine.stock <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Medicine is out of stock"
        )
        
    # Check if medicine is already in user's cart
    cart_item = db.query(CartItem).filter(
        CartItem.user_id == current_user.id,
        CartItem.medicine_id == item_in.medicine_id
    ).first()
    
    if cart_item:
        new_qty = cart_item.quantity + item_in.quantity
        if new_qty > medicine.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({new_qty}) exceeds available stock ({medicine.stock})"
            )
        cart_item.quantity = new_qty
    else:
        if item_in.quantity > medicine.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Requested quantity ({item_in.quantity}) exceeds available stock ({medicine.stock})"
            )
        cart_item = CartItem(
            user_id=current_user.id,
            medicine_id=item_in.medicine_id,
            quantity=item_in.quantity
        )
        db.add(cart_item)
        
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.get("", response_model=CartOut)
def get_cart(
    user_id: Optional[int] = None,
    distance: int = Query(0, ge=0),
    coupon_code: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch the shopping cart details including the dynamic fees and items.
    Accepts both user_id query parameter and token-extracted security credentials.
    """
    # Enforce token security for the logged-in user context
    effective_user_id = current_user.id
    if user_id and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this user's cart."
        )
        
    cart_items = db.query(CartItem).filter(CartItem.user_id == effective_user_id).all()
    
    # Calculate cart details
    details = calculate_cart_details(cart_items, distance, coupon_code, db)
    
    return CartOut(
        items=cart_items,
        **details
    )

@router.patch("/items/{id}", response_model=CartItemOut)
def update_cart_item(
    id: int,
    item_update: CartItemUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the quantity of a cart item.
    Accepts either the database record ID or the medicine ID for resilience.
    """
    # Defensive lookup: search by cart item ID first, then by medicine ID
    cart_item = db.query(CartItem).filter(
        CartItem.id == id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        cart_item = db.query(CartItem).filter(
            CartItem.medicine_id == id,
            CartItem.user_id == current_user.id
        ).first()
        
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        
    medicine = db.query(Medicine).filter(Medicine.id == cart_item.medicine_id).first()
    if not medicine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Medicine associated with cart item not found")
        
    if item_update.quantity > medicine.stock:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Requested quantity ({item_update.quantity}) exceeds available stock ({medicine.stock})"
        )
        
    cart_item.quantity = item_update.quantity
    db.commit()
    db.refresh(cart_item)
    return cart_item

@router.delete("/items/{id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_from_cart(
    id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Remove an item from the shopping cart.
    Accepts either database record ID or medicine ID for absolute resilience.
    """
    cart_item = db.query(CartItem).filter(
        CartItem.id == id,
        CartItem.user_id == current_user.id
    ).first()
    
    if not cart_item:
        cart_item = db.query(CartItem).filter(
            CartItem.medicine_id == id,
            CartItem.user_id == current_user.id
        ).first()
        
    if not cart_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cart item not found")
        
    db.delete(cart_item)
    db.commit()
    return None
