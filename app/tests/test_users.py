def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_admin_can_list_users(client, admin_token):
    resp = client.get("/api/v1/users/", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert "total" in data


def test_viewer_cannot_list_users(client, viewer_token):
    resp = client.get("/api/v1/users/", headers=auth(viewer_token))
    assert resp.status_code == 403


def test_analyst_cannot_list_users(client, analyst_token):
    resp = client.get("/api/v1/users/", headers=auth(analyst_token))
    assert resp.status_code == 403


def test_admin_can_create_user(client, admin_token):
    resp = client.post(
        "/api/v1/users/",
        headers=auth(admin_token),
        json={
            "name": "New Viewer",
            "email": "newviewer@test.com",
            "password": "password123",
            "role": "viewer",
        },
    )
    assert resp.status_code == 201
    assert resp.json()["email"] == "newviewer@test.com"


def test_duplicate_email_rejected(client, admin_token, admin_user):
    resp = client.post(
        "/api/v1/users/",
        headers=auth(admin_token),
        json={
            "name": "Duplicate",
            "email": "admin@test.com",
            "password": "password123",
            "role": "viewer",
        },
    )
    assert resp.status_code == 409


def test_admin_can_update_user_role(client, admin_token, viewer_user):
    resp = client.patch(
        f"/api/v1/users/{viewer_user.id}",
        headers=auth(admin_token),
        json={"role": "analyst"},
    )
    assert resp.status_code == 200
    assert resp.json()["role"] == "analyst"


def test_admin_can_deactivate_user(client, admin_token, viewer_user):
    resp = client.patch(
        f"/api/v1/users/{viewer_user.id}",
        headers=auth(admin_token),
        json={"is_active": False},
    )
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


def test_admin_can_soft_delete_user(client, admin_token, viewer_user):
    resp = client.delete(
        f"/api/v1/users/{viewer_user.id}",
        headers=auth(admin_token),
    )
    assert resp.status_code == 204


def test_short_password_rejected(client, admin_token):
    resp = client.post(
        "/api/v1/users/",
        headers=auth(admin_token),
        json={"name": "Bad User", "email": "bad@test.com", "password": "abc"},
    )
    assert resp.status_code == 422
