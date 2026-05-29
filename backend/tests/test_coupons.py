import pytest

def test_apply_flat_coupon_success(client, seed_data, auth_headers):
    # Add Amoxicillin (ID: 3, price=120) * 3 = 360 (meets min_cart_value of 299 for FLAT50)
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 3}, headers=auth_headers)
    
    response = client.post(
        "/coupons/apply",
        json={"code": "FLAT50"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert float(data["discount_amount"]) == 50.00
    assert "saved ₹50.00" in data["message"].lower()

def test_apply_percentage_coupon_success(client, seed_data, auth_headers):
    # Add Amoxicillin (ID: 3, price=120) * 2 = 240 (meets min_cart_value of 199 for PCT20)
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 2}, headers=auth_headers)
    
    response = client.post(
        "/coupons/apply",
        json={"code": "PCT20"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert float(data["discount_amount"]) == 48.00 # 20% of 240

def test_apply_coupon_invalid_code(client, seed_data, auth_headers):
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 5}, headers=auth_headers)
    
    response = client.post(
        "/coupons/apply",
        json={"code": "NONEXISTENT"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert float(data["discount_amount"]) == 0.00
    assert "invalid" in data["message"].lower()

def test_apply_coupon_expired(client, seed_data, auth_headers):
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 3}, headers=auth_headers)
    
    response = client.post(
        "/coupons/apply",
        json={"code": "EXPIRED"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert float(data["discount_amount"]) == 0.00
    assert "expired" in data["message"].lower()

def test_apply_coupon_inactive(client, seed_data, auth_headers):
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 3}, headers=auth_headers)
    
    response = client.post(
        "/coupons/apply",
        json={"code": "INACTIVE"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert float(data["discount_amount"]) == 0.00
    assert "no longer active" in data["message"].lower()

def test_apply_coupon_min_value_not_met(client, seed_data, auth_headers):
    # Add Paracetamol (ID: 1, price=15) * 2 = 30 (does not meet min_cart_value 299 for FLAT50)
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 2}, headers=auth_headers)
    
    response = client.post(
        "/coupons/apply",
        json={"code": "FLAT50"},
        headers=auth_headers
    )
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert float(data["discount_amount"]) == 0.00
    assert "minimum cart value of" in data["message"].lower()
