import pytest
from unittest.mock import patch
from app.models import Medicine, CartItem, Order

@patch("app.routers.cart.is_late_night", return_value=False)
def test_order_placement_success(mock_late_night, client, seed_data, auth_headers, db_session):
    # 1. Add item to cart
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 3}, headers=auth_headers) # Paracetamol, price=15, stock=100
    
    # Verify stock before order
    med_before = db_session.query(Medicine).filter(Medicine.id == 1).first()
    assert med_before.stock == 100
    
    # 2. Place order (distance=1500, pincode="560001")
    response = client.post(
        "/orders",
        json={"pincode": "560001", "distance": 1500, "coupon_code": None},
        headers=auth_headers
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "placed"
    assert data["pincode"] == "560001"
    assert data["distance"] == 1500
    assert float(data["item_total"]) == 45.00 # 15 * 3
    assert float(data["total_payable"]) == 74.00 # 45 + 29 (small cart) + 0 (delivery <= 2000m) + 0 (day time)
    
    # Verify stock has been reduced by 3
    db_session.expire_all()
    med_after = db_session.query(Medicine).filter(Medicine.id == 1).first()
    assert med_after.stock == 97
    
    # Verify user's cart has been cleared
    cart_items = db_session.query(CartItem).filter(CartItem.user_id == 999).all()
    assert len(cart_items) == 0

def test_order_placement_empty_cart(client, seed_data, auth_headers):
    # Try placing order with empty cart
    response = client.post(
        "/orders",
        json={"pincode": "560001", "distance": 1500},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "cart is empty" in response.json()["detail"].lower()

def test_order_placement_unserviceable_address(client, seed_data, auth_headers):
    # Add item
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 1}, headers=auth_headers)
    
    # Try placing order with distance > 5000m
    response = client.post(
        "/orders",
        json={"pincode": "560001", "distance": 6000},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "distance is not serviceable" in response.json()["detail"].lower()

def test_order_placement_exceeds_stock_at_placement(client, seed_data, auth_headers, db_session):
    # Add Ibuprofen (ID: 2, stock=5)
    client.post("/cart/items", json={"medicine_id": 2, "quantity": 4}, headers=auth_headers)
    
    # Simulate database stock reducing outside user cart (e.g. concurrent order reduces stock to 2)
    ibu = db_session.query(Medicine).filter(Medicine.id == 2).first()
    ibu.stock = 2
    db_session.commit()
    
    # Now try to place the order with quantity 4 (which exceeds new stock 2)
    response = client.post(
        "/orders",
        json={"pincode": "560001", "distance": 1000},
        headers=auth_headers
    )
    
    assert response.status_code == 400
    assert "are available, requested" in response.json()["detail"].lower()
