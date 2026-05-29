import pytest

def test_serviceability_within_2000m(client):
    response = client.post(
        "/serviceability/check",
        json={"pincode": "560001", "distance": 1500}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["serviceable"] is True
    assert data["distance"] == 1500
    assert data["estimated_delivery_minutes"] == 30

def test_serviceability_exactly_2000m(client):
    response = client.post(
        "/serviceability/check",
        json={"pincode": "560001", "distance": 2000}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["serviceable"] is True
    assert data["distance"] == 2000
    assert data["estimated_delivery_minutes"] == 30

def test_serviceability_between_2001m_and_5000m(client):
    response = client.post(
        "/serviceability/check",
        json={"pincode": "560001", "distance": 3500}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["serviceable"] is True
    assert data["distance"] == 3500
    assert data["estimated_delivery_minutes"] == 45

def test_serviceability_exactly_5000m(client):
    response = client.post(
        "/serviceability/check",
        json={"pincode": "560001", "distance": 5000}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["serviceable"] is True
    assert data["distance"] == 5000
    assert data["estimated_delivery_minutes"] == 45

def test_serviceability_exceeds_5000m(client):
    response = client.post(
        "/serviceability/check",
        json={"pincode": "560001", "distance": 5001}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["serviceable"] is False
    assert data["estimated_delivery_minutes"] is None
