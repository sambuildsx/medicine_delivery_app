from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from decimal import Decimal
from app.database import get_db
from app.models import CartItem, Medicine, Order, OrderItem, Coupon
from app.schemas import OrderPlace, OrderOut
from app.auth import get_current_user, User
from app.routers.cart import calculate_cart_details

router = APIRouter(prefix="/orders", tags=["Orders"])

@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
def place_order(
    order_in: OrderPlace,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Place a new order for the authenticated user.
    - Locks medicine rows to prevent concurrent stock race conditions (double spending).
    - Validates cart contents, serviceability, stock levels, and coupons.
    - Computes exact fees and discounts, writes order & items, reduces stock, and clears the cart.
    """
    user_id = current_user.id
    
    # 1. Check if the address is serviceable
    if order_in.distance > 5000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Distance is not serviceable. Max delivery distance is 5000 meters."
        )
        
    # Determine estimated delivery time
    est_minutes = 30 if order_in.distance <= 2000 else 45
    
    # Start transaction locking
    # 2. Fetch user's cart items
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    if not cart_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot place order. Your shopping cart is empty."
        )
        
    # 3. Lock medicine rows and validate stocks
    # Using `with_for_update` to prevent concurrent stock modifications
    for item in cart_items:
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).with_for_update().first()
        if not medicine:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medicine id {item.medicine_id} not found."
            )
        if medicine.stock <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Medicine '{medicine.name}' is out of stock."
            )
        if item.quantity > medicine.stock:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Only {medicine.stock} units of '{medicine.name}' are available, requested {item.quantity}."
            )

    # 4. Calculate final payable details including dynamic fees and coupons
    details = calculate_cart_details(cart_items, order_in.distance, order_in.coupon_code, db)
    
    # 5. Create Order record
    new_order = Order(
        user_id=user_id,
        status="placed",
        pincode=order_in.pincode,
        distance=order_in.distance,
        estimated_delivery_minutes=est_minutes,
        item_total=details["item_total"],
        discount_amount=details["discount_amount"],
        small_cart_fee=details["small_cart_fee"],
        delivery_fee=details["delivery_fee"],
        late_night_fee=details["late_night_fee"],
        total_payable=details["total_payable"],
        coupon_applied=details["coupon_applied"]
    )
    
    db.add(new_order)
    db.flush() # Populate new_order.id
    
    # 6. Create Order Items and decrease stock
    for item in cart_items:
        # Re-fetch locked medicine row
        medicine = db.query(Medicine).filter(Medicine.id == item.medicine_id).with_for_update().first()
        
        # Capture snapshot of medicine at purchase time
        order_item = OrderItem(
            order_id=new_order.id,
            medicine_id=item.medicine_id,
            quantity=item.quantity,
            name=medicine.name,
            salt_composition=medicine.salt_composition,
            selling_price=Decimal(str(medicine.selling_price))
        )
        db.add(order_item)
        
        # Deduct stock
        medicine.stock -= item.quantity
        
    # 7. Clear the shopping cart
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    
    # Commit all changes atomically
    db.commit()
    db.refresh(new_order)
    
    return new_order

@router.get("", response_model=List[OrderOut])
def get_order_history(
    user_id: Optional[int] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get order history for the authenticated user.
    Accepts both user_id query parameter and token-extracted security credentials.
    """
    effective_user_id = current_user.id
    if user_id and user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this user's order history."
        )
        
    orders = db.query(Order).filter(Order.user_id == effective_user_id).order_by(Order.created_at.desc()).all()
    return orders

@router.get("/{order_id}", response_model=OrderOut)
def get_order_detail(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get the detail of a specific order."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found."
        )
        
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to view this order's details."
        )
        
    return order
