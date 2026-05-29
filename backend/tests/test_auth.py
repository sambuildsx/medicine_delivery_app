import pytest

def test_register_success(client):
    response = client.post(
        "/auth/register",
        json={"email": "new.user@example.com", "password": "securepassword", "full_name": "New User"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "new.user@example.com"
    assert data["full_name"] == "New User"

def test_register_duplicate_email(client, auth_headers):
    # Register again with duplicate test.user@example.com (created by auth_headers fixture)
    response = client.post(
        "/auth/register",
        json={"email": "test.user@example.com", "password": "anotherpassword", "full_name": "Duplicate User"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email already registered"

def test_login_success(client, auth_headers):
    response = client.post(
        "/auth/login",
        json={"email": "test.user@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["email"] == "test.user@example.com"
    assert data["full_name"] == "Test User"

def test_login_wrong_password(client, auth_headers):
    response = client.post(
        "/auth/login",
        json={"email": "test.user@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password"
