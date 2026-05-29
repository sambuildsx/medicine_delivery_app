import pytest
from unittest.mock import patch

def test_add_to_cart_success(client, seed_data, auth_headers):
    # Add Paracetamol (ID: 1)
    response = client.post(
        "/cart/items",
        json={"medicine_id": 1, "quantity": 2},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["medicine_id"] == 1
    assert data["quantity"] == 2

def test_add_to_cart_oos(client, seed_data, auth_headers):
    # Add Ranitidine (ID: 4, stock=0)
    response = client.post(
        "/cart/items",
        json={"medicine_id": 4, "quantity": 1},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "out of stock" in response.json()["detail"].lower()

def test_add_to_cart_exceeds_stock(client, seed_data, auth_headers):
    # Add Ibuprofen (ID: 2, stock=5, try adding 6)
    response = client.post(
        "/cart/items",
        json={"medicine_id": 2, "quantity": 6},
        headers=auth_headers
    )
    assert response.status_code == 400
    assert "exceeds available stock" in response.json()["detail"].lower()

def test_add_same_medicine_increments_quantity(client, seed_data, auth_headers):
    # Add 1 Paracetamol
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 1}, headers=auth_headers)
    # Add 2 more Paracetamol
    response = client.post("/cart/items", json={"medicine_id": 1, "quantity": 2}, headers=auth_headers)
    
    assert response.status_code == 201
    assert response.json()["quantity"] == 3

# --- FEE CALCULATIONS TESTS ---

@patch("app.routers.cart.is_late_night", return_value=False)
def test_fees_none_applied(mock_late_night, client, seed_data, auth_headers):
    # Add Amoxicillin (ID: 3, price=120) * 2 = 240 (Item Total >= 199, Distance = 0, Day Time)
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 2}, headers=auth_headers)
    
    response = client.get("/cart?distance=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["item_total"]) == 240.00
    assert float(data["small_cart_fee"]) == 0.00
    assert float(data["delivery_fee"]) == 0.00
    assert float(data["late_night_fee"]) == 0.00
    assert float(data["total_payable"]) == 240.00

@patch("app.routers.cart.is_late_night", return_value=False)
def test_small_cart_fee_only(mock_late_night, client, seed_data, auth_headers):
    # Add Paracetamol (ID: 1, price=15) * 2 = 30 (Item Total < 199, Day time, Distance = 0)
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 2}, headers=auth_headers)
    
    response = client.get("/cart?distance=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["item_total"]) == 30.00
    assert float(data["small_cart_fee"]) == 29.00
    assert float(data["delivery_fee"]) == 0.00
    assert float(data["late_night_fee"]) == 0.00
    assert float(data["total_payable"]) == 59.00

@patch("app.routers.cart.is_late_night", return_value=False)
def test_delivery_fee_only(mock_late_night, client, seed_data, auth_headers):
    # Add Amoxicillin (ID: 3, price=120) * 2 = 240 (Subtotal >= 199, Distance = 2500 > 2000m)
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 2}, headers=auth_headers)
    
    response = client.get("/cart?distance=2500", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["item_total"]) == 240.00
    assert float(data["small_cart_fee"]) == 0.00
    assert float(data["delivery_fee"]) == 40.00
    assert float(data["late_night_fee"]) == 0.00
    assert float(data["total_payable"]) == 280.00

@patch("app.routers.cart.is_late_night", return_value=True)
def test_late_night_fee_only(mock_late_night, client, seed_data, auth_headers):
    # Add Amoxicillin (ID: 3, price=120) * 2 = 240 (Subtotal >= 199, Distance = 0, Late night)
    client.post("/cart/items", json={"medicine_id": 3, "quantity": 2}, headers=auth_headers)
    
    response = client.get("/cart?distance=0", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["item_total"]) == 240.00
    assert float(data["small_cart_fee"]) == 0.00
    assert float(data["delivery_fee"]) == 0.00
    assert float(data["late_night_fee"]) == 25.00
    assert float(data["total_payable"]) == 265.00

@patch("app.routers.cart.is_late_night", return_value=True)
def test_all_fees_simultaneously(mock_late_night, client, seed_data, auth_headers):
    # Add Paracetamol (ID: 1, price=15) * 2 = 30 (Subtotal < 199, Distance = 3000 > 2000m, Late night)
    client.post("/cart/items", json={"medicine_id": 1, "quantity": 2}, headers=auth_headers)
    
    response = client.get("/cart?distance=3000", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert float(data["item_total"]) == 30.00
    assert float(data["small_cart_fee"]) == 29.00
    assert float(data["delivery_fee"]) == 40.00
    assert float(data["late_night_fee"]) == 25.00
    assert float(data["total_payable"]) == 124.00 # 30 + 29 + 40 + 25
