import pytest
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app.models import User, Medicine, Coupon, CartItem, Order, OrderItem

from app.auth import get_password_hash, create_access_token

# Setup in-memory SQLite for complete test isolation using shared memory URI
SQLALCHEMY_DATABASE_URL = "sqlite:///file:testdb?mode=memory&cache=shared"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False, "uri": True}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database structure for each test function run."""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """Create a TestClient that overrides the get_db dependency to use the isolated test database session."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def seed_data(db_session):
    """Seed key medicines and coupons for testing purposes."""
    # Medicines
    paracetamol = Medicine(id=1, name="Paracetamol 500mg", salt_composition="Paracetamol", mrp=Decimal("20.00"), selling_price=Decimal("15.00"), stock=100, prescription_required=False)
    ibuprofen = Medicine(id=2, name="Ibuprofen 400mg", salt_composition="Ibuprofen", mrp=Decimal("30.00"), selling_price=Decimal("25.00"), stock=5, prescription_required=False)
    amoxicillin = Medicine(id=3, name="Amoxicillin 500mg", salt_composition="Amoxicillin", mrp=Decimal("150.00"), selling_price=Decimal("120.00"), stock=50, prescription_required=True)
    oos_med = Medicine(id=4, name="Ranitidine 150mg (OOS)", salt_composition="Ranitidine", mrp=Decimal("18.00"), selling_price=Decimal("12.00"), stock=0, prescription_required=False)
    
    db_session.add_all([paracetamol, ibuprofen, amoxicillin, oos_med])
    
    # Coupons
    future_date = datetime.now(timezone.utc) + timedelta(days=10)
    past_date = datetime.now(timezone.utc) - timedelta(days=2)
    
    flat50 = Coupon(id=1, code="FLAT50", discount_type="flat", discount_value=Decimal("50.00"), min_cart_value=Decimal("299.00"), expires_at=future_date, is_active=True)
    pct20 = Coupon(id=2, code="PCT20", discount_type="percentage", discount_value=Decimal("20.00"), min_cart_value=Decimal("199.00"), expires_at=future_date, is_active=True)
    expired = Coupon(id=3, code="EXPIRED", discount_type="flat", discount_value=Decimal("10.00"), min_cart_value=Decimal("50.00"), expires_at=past_date, is_active=True)
    inactive = Coupon(id=4, code="INACTIVE", discount_type="flat", discount_value=Decimal("15.00"), min_cart_value=Decimal("50.00"), expires_at=future_date, is_active=False)
    
    db_session.add_all([flat50, pct20, expired, inactive])
    db_session.commit()

@pytest.fixture(scope="function")
def auth_headers(db_session):
    """Create a default test user and return authorization header token."""
    pwd_hash = get_password_hash("password123")
    user = User(id=999, email="test.user@example.com", password_hash=pwd_hash, full_name="Test User")
    db_session.add(user)
    db_session.commit()
    
    # Generate token
    token = create_access_token({"user_id": user.id, "email": user.email})
    return {"Authorization": f"Bearer {token}"}
