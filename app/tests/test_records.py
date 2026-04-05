from datetime import datetime, timezone


def auth(token):
    return {"Authorization": f"Bearer {token}"}


SAMPLE_RECORD = {
    "amount": 5000.00,
    "type": "income",
    "category": "salary",
    "date": "2024-06-01T00:00:00Z",
    "notes": "Monthly salary",
}


def test_admin_can_create_record(client, admin_token):
    resp = client.post("/api/v1/records/", headers=auth(admin_token), json=SAMPLE_RECORD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["amount"] == 5000.00
    assert data["type"] == "income"
    assert data["category"] == "salary"


def test_viewer_cannot_create_record(client, viewer_token):
    resp = client.post("/api/v1/records/", headers=auth(viewer_token), json=SAMPLE_RECORD)
    assert resp.status_code == 403


def test_analyst_cannot_create_record(client, analyst_token):
    resp = client.post("/api/v1/records/", headers=auth(analyst_token), json=SAMPLE_RECORD)
    assert resp.status_code == 403


def test_all_roles_can_list_records(client, admin_token, analyst_token, viewer_token):
    for token in [admin_token, analyst_token, viewer_token]:
        resp = client.get("/api/v1/records/", headers=auth(token))
        assert resp.status_code == 200


def test_list_records_filter_by_type(client, admin_token):
    client.post("/api/v1/records/", headers=auth(admin_token), json=SAMPLE_RECORD)
    client.post(
        "/api/v1/records/",
        headers=auth(admin_token),
        json={**SAMPLE_RECORD, "type": "expense", "category": "food", "amount": 200},
    )

    resp = client.get("/api/v1/records/?type=income", headers=auth(admin_token))
    assert resp.status_code == 200
    items = resp.json()["items"]
    assert all(r["type"] == "income" for r in items)


def test_list_records_pagination(client, admin_token):
    for i in range(5):
        client.post(
            "/api/v1/records/",
            headers=auth(admin_token),
            json={**SAMPLE_RECORD, "amount": 100 * (i + 1)},
        )

    resp = client.get("/api/v1/records/?page=1&page_size=2", headers=auth(admin_token))
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["items"]) == 2
    assert data["total"] == 5


def test_admin_can_update_record(client, admin_token):
    create_resp = client.post("/api/v1/records/", headers=auth(admin_token), json=SAMPLE_RECORD)
    record_id = create_resp.json()["id"]

    update_resp = client.patch(
        f"/api/v1/records/{record_id}",
        headers=auth(admin_token),
        json={"amount": 6000.00, "notes": "Updated salary"},
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["amount"] == 6000.00


def test_admin_can_soft_delete_record(client, admin_token):
    create_resp = client.post("/api/v1/records/", headers=auth(admin_token), json=SAMPLE_RECORD)
    record_id = create_resp.json()["id"]

    del_resp = client.delete(f"/api/v1/records/{record_id}", headers=auth(admin_token))
    assert del_resp.status_code == 204

    # Deleted record should not appear in listing
    list_resp = client.get("/api/v1/records/", headers=auth(admin_token))
    ids = [r["id"] for r in list_resp.json()["items"]]
    assert record_id not in ids


def test_negative_amount_rejected(client, admin_token):
    resp = client.post(
        "/api/v1/records/",
        headers=auth(admin_token),
        json={**SAMPLE_RECORD, "amount": -100},
    )
    assert resp.status_code == 422


def test_get_nonexistent_record_returns_404(client, viewer_token):
    resp = client.get("/api/v1/records/99999", headers=auth(viewer_token))
    assert resp.status_code == 404
