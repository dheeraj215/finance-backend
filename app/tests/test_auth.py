from app.tests.conftest import get_token


def test_login_success(client, admin_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "password123"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["role"] == "admin"


def test_login_wrong_password(client, admin_user):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@test.com", "password": "wrongpassword"},
    )
    assert resp.status_code == 401


def test_login_unknown_email(client):
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": "nobody@test.com", "password": "password123"},
    )
    assert resp.status_code == 401


def test_get_me(client, admin_token):
    resp = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.com"


def test_get_me_no_token(client):
    resp = client.get("/api/v1/users/me")
    assert resp.status_code == 403
