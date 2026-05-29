from datetime import datetime, timezone, timedelta
from decimal import Decimal
from sqlalchemy.orm import Session
from app.database import SessionLocal, Base, engine
from app.models import User, Medicine, Coupon
from app.auth import get_password_hash

def seed_db(db: Session):
    """Seed the database with users, medicines, and coupons if they don't already exist."""
    print("Database seeding check...")
    
    # 1. Seed Users (5+)
    if db.query(User).count() == 0:
        print("Seeding users...")
        users = [
            User(email="john.doe@example.com", password_hash=get_password_hash("password123"), full_name="John Doe"),
            User(email="jane.smith@example.com", password_hash=get_password_hash("password123"), full_name="Jane Smith"),
            User(email="sam.jones@example.com", password_hash=get_password_hash("password123"), full_name="Sam Jones"),
            User(email="alice.williams@example.com", password_hash=get_password_hash("password123"), full_name="Alice Williams"),
            User(email="bob.brown@example.com", password_hash=get_password_hash("password123"), full_name="Bob Brown"),
        ]
        db.add_all(users)
        db.commit()
        print("Users seeded successfully.")

    # 2. Seed Medicines (20+)
    if db.query(Medicine).count() == 0:
        print("Seeding medicines...")
        medicines = [
            Medicine(name="Paracetamol 500mg", salt_composition="Paracetamol", mrp=Decimal("20.00"), selling_price=Decimal("15.00"), stock=120, prescription_required=False),
            Medicine(name="Ibuprofen 400mg", salt_composition="Ibuprofen", mrp=Decimal("30.00"), selling_price=Decimal("25.00"), stock=80, prescription_required=False),
            Medicine(name="Amoxicillin 500mg", salt_composition="Amoxicillin Trihydrate", mrp=Decimal("150.00"), selling_price=Decimal("120.00"), stock=50, prescription_required=True),
            Medicine(name="Atorvastatin 10mg", salt_composition="Atorvastatin", mrp=Decimal("220.00"), selling_price=Decimal("180.00"), stock=40, prescription_required=True),
            Medicine(name="Metformin 500mg", salt_composition="Metformin Hydrochloride", mrp=Decimal("60.00"), selling_price=Decimal("45.00"), stock=60, prescription_required=True),
            Medicine(name="Cetirizine 10mg", salt_composition="Cetirizine Dihydrochloride", mrp=Decimal("24.00"), selling_price=Decimal("18.00"), stock=100, prescription_required=False),
            Medicine(name="Pantoprazole 40mg", salt_composition="Pantoprazole Sodium", mrp=Decimal("90.00"), selling_price=Decimal("70.00"), stock=90, prescription_required=True),
            Medicine(name="Azithromycin 500mg", salt_composition="Azithromycin Dihydrate", mrp=Decimal("140.00"), selling_price=Decimal("110.00"), stock=30, prescription_required=True),
            Medicine(name="Vitamin C 500mg", salt_composition="Ascorbic Acid", mrp=Decimal("50.00"), selling_price=Decimal("35.00"), stock=200, prescription_required=False),
            Medicine(name="Vitamin D3 60k IU", salt_composition="Cholecalciferol", mrp=Decimal("120.00"), selling_price=Decimal("90.00"), stock=150, prescription_required=False),
            Medicine(name="Amlodipine 5mg", salt_composition="Amlodipine Besylate", mrp=Decimal("40.00"), selling_price=Decimal("30.00"), stock=75, prescription_required=True),
            Medicine(name="Losartan 50mg", salt_composition="Losartan Potassium", mrp=Decimal("110.00"), selling_price=Decimal("85.00"), stock=55, prescription_required=True),
            Medicine(name="Montelukast 10mg", salt_composition="Montelukast Sodium", mrp=Decimal("165.00"), selling_price=Decimal("130.00"), stock=45, prescription_required=True),
            Medicine(name="Omeprazole 20mg", salt_composition="Omeprazole Magnesium", mrp=Decimal("75.00"), selling_price=Decimal("55.00"), stock=110, prescription_required=False),
            # OUT OF STOCK MEDICINE to verify cart validation rules
            Medicine(name="Ranitidine 150mg (OOS)", salt_composition="Ranitidine Hydrochloride", mrp=Decimal("18.00"), selling_price=Decimal("12.00"), stock=0, prescription_required=False),
            Medicine(name="Levothyroxine 50mcg", salt_composition="Levothyroxine Sodium", mrp=Decimal("175.00"), selling_price=Decimal("140.00"), stock=100, prescription_required=True),
            Medicine(name="Cough Syrup 100ml", salt_composition="Dextromethorphan + Chlorpheniramine", mrp=Decimal("105.00"), selling_price=Decimal("85.00"), stock=65, prescription_required=False),
            Medicine(name="Eye Drops 10ml", salt_composition="Carboxymethylcellulose Sodium", mrp=Decimal("120.00"), selling_price=Decimal("95.00"), stock=50, prescription_required=False),
            Medicine(name="Antiseptic Liquid 250ml", salt_composition="Chlorhexidine Gluconate + Cetrimide", mrp=Decimal("180.00"), selling_price=Decimal("160.00"), stock=85, prescription_required=False),
            Medicine(name="Salbutamol Inhaler", salt_composition="Salbutamol Sulphate", mrp=Decimal("250.00"), selling_price=Decimal("210.00"), stock=25, prescription_required=True),
            Medicine(name="Insulin Glargine Pen", salt_composition="Insulin Glargine", mrp=Decimal("1200.00"), selling_price=Decimal("950.00"), stock=15, prescription_required=True),
        ]
        db.add_all(medicines)
        db.commit()
        print("Medicines seeded successfully.")

    # 3. Seed Coupons dynamically checking by code
    print("Seeding coupons...")
    future_date = datetime.now(timezone.utc) + timedelta(days=365)
    seed_coupons = [
        {"code": "FLAT50", "discount_type": "flat", "discount_value": Decimal("50.00"), "min_cart_value": Decimal("299.00")},
        {"code": "PCT20", "discount_type": "percentage", "discount_value": Decimal("20.00"), "min_cart_value": Decimal("199.00")},
        # Welcoming coupon for new users: flat ₹100 off on minimum purchase of ₹199
        {"code": "NEWUSER", "discount_type": "flat", "discount_value": Decimal("100.00"), "min_cart_value": Decimal("199.00")},
        # Value coupon: 15% off on minimum purchase of ₹500
        {"code": "SAVE15", "discount_type": "percentage", "discount_value": Decimal("15.00"), "min_cart_value": Decimal("500.00")},
    ]
    
    for c_info in seed_coupons:
        existing = db.query(Coupon).filter(Coupon.code == c_info["code"]).first()
        if not existing:
            new_coupon = Coupon(
                code=c_info["code"],
                discount_type=c_info["discount_type"],
                discount_value=c_info["discount_value"],
                min_cart_value=c_info["min_cart_value"],
                expires_at=future_date,
                is_active=True
            )
            db.add(new_coupon)
    db.commit()
    print("Coupons seeded successfully.")

        
    print("Database seeding check completed.")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        # Create tables
        Base.metadata.create_all(bind=engine)
        seed_db(db)
    finally:
        db.close()
