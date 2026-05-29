from sqlalchemy import Column, Integer, String, Boolean, Numeric, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cart_items = relationship("CartItem", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")

class Medicine(Base):
    __tablename__ = "medicines"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    salt_composition = Column(String(255), index=True, nullable=False)
    mrp = Column(Numeric(10, 2), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False, default=0)
    prescription_required = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    cart_entries = relationship("CartItem", back_populates="medicine", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Establish relationships
    user = relationship("User", back_populates="cart_items")
    medicine = relationship("Medicine", back_populates="cart_entries")
    
    # Enforce uniqueness of user_id + medicine_id in python
    __table_args__ = (UniqueConstraint("user_id", "medicine_id", name="unique_user_medicine"),)

class Coupon(Base):
    __tablename__ = "coupons"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False)
    discount_type = Column(String(20), nullable=False) # 'flat' or 'percentage'
    discount_value = Column(Numeric(10, 2), nullable=False)
    min_cart_value = Column(Numeric(10, 2), nullable=False, default=0.00)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="placed")
    pincode = Column(String(20), nullable=False)
    distance = Column(Integer, nullable=False) # in meters
    estimated_delivery_minutes = Column(Integer, nullable=False)
    item_total = Column(Numeric(10, 2), nullable=False)
    discount_amount = Column(Numeric(10, 2), nullable=False, default=0.00)
    small_cart_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    delivery_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    late_night_fee = Column(Numeric(10, 2), nullable=False, default=0.00)
    total_payable = Column(Numeric(10, 2), nullable=False)
    coupon_applied = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    medicine_id = Column(Integer, ForeignKey("medicines.id", ondelete="SET NULL"), nullable=True)
    quantity = Column(Integer, nullable=False)
    name = Column(String(255), nullable=False)
    salt_composition = Column(String(255), nullable=False)
    selling_price = Column(Numeric(10, 2), nullable=False)
    
    order = relationship("Order", back_populates="items")
