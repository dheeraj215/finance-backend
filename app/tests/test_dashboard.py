def auth(token):
    return {"Authorization": f"Bearer {token}"}


INCOME = {
    "amount": 8000.00,
    "type": "income",
    "category": "salary",
    "date": "2024-06-01T00:00:00Z",
}

EXPENSE = {
    "amount": 1500.00,
    "type": "expense",
    "category": "rent",
    "date": "2024-06-02T00:00:00Z",
}


def seed_records(client, admin_token):
    client.post("/api/v1/records/", headers=auth(admin_token), json=INCOME)
    client.post("/api/v1/records/", headers=auth(admin_token), json=EXPENSE)


def test_admin_can_view_dashboard(client, admin_token):
    seed_records(client, admin_token)
    resp = client.get("/api/v1/dashboard/summary", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_income"] == 8000.00
    assert data["total_expenses"] == 1500.00
    assert data["net_balance"] == 6500.00


def test_analyst_can_view_dashboard(client, analyst_token, admin_token):
    seed_records(client, admin_token)
    resp = client.get("/api/v1/dashboard/summary", headers=auth(analyst_token))
    assert resp.status_code == 200


def test_viewer_cannot_view_dashboard(client, viewer_token):
    resp = client.get("/api/v1/dashboard/summary", headers=auth(viewer_token))
    assert resp.status_code == 403


def test_dashboard_category_totals(client, admin_token):
    seed_records(client, admin_token)
    resp = client.get("/api/v1/dashboard/summary", headers=auth(admin_token))
    assert resp.status_code == 200
    categories = {c["category"] for c in resp.json()["category_totals"]}
    assert "salary" in categories
    assert "rent" in categories


def test_dashboard_recent_activity_limit(client, admin_token):
    for i in range(12):
        client.post(
            "/api/v1/records/",
            headers=auth(admin_token),
            json={**INCOME, "amount": 100 * (i + 1)},
        )
    resp = client.get("/api/v1/dashboard/summary", headers=auth(admin_token))
    assert len(resp.json()["recent_activity"]) <= 10


def test_empty_dashboard(client, admin_token):
    resp = client.get("/api/v1/dashboard/summary", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_income"] == 0.0
    assert data["total_expenses"] == 0.0
    assert data["net_balance"] == 0.0
