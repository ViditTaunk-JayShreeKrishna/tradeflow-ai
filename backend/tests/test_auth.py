import pytest

TEST_USER = {
    "email": "testci@tradeflow.com",
    "full_name": "CI Test User",
    "password": "testpassword123",
}


def test_register_user(client):
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == TEST_USER["email"]
    assert data["full_name"] == TEST_USER["full_name"]
    assert "hashed_password" not in data
    assert data["is_active"] is True


def test_register_duplicate_email(client):
    client.post("/auth/register", json=TEST_USER)
    response = client.post("/auth/register", json=TEST_USER)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_success(client):
    client.post("/auth/register", json=TEST_USER)
    response = client.post("/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client):
    client.post("/auth/register", json=TEST_USER)
    response = client.post("/auth/login", json={
        "email": TEST_USER["email"],
        "password": "wrongpassword",
    })
    assert response.status_code == 401


def test_get_me(client):
    client.post("/auth/register", json=TEST_USER)
    login = client.post("/auth/login", json={
        "email": TEST_USER["email"],
        "password": TEST_USER["password"],
    })
    token = login.json()["access_token"]
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == TEST_USER["email"]


def test_get_me_unauthorized(client):
    response = client.get("/auth/me")
    assert response.status_code == 401


def test_hs_classifier_status(client):
    response = client.get("/hs-classifier/status")
    assert response.status_code == 200
    data = response.json()
    assert "model_ready" in data