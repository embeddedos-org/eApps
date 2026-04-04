"""Integration tests for the REST API."""


def test_health(app_client):
    resp = app_client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


def test_register_and_login(app_client):
    resp = app_client.post("/auth/register", json={
        "username": "testuser", "password": "testpass123", "role": "read_write",
    })
    assert resp.status_code == 201
    assert resp.json()["username"] == "testuser"

    resp = app_client.post("/auth/login", json={"username": "testuser", "password": "testpass123"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(app_client):
    resp = app_client.post("/auth/login", json={"username": "admin", "password": "wrongpass"})
    assert resp.status_code == 401


def test_get_me(app_client, admin_token):
    resp = app_client.get("/auth/me", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200
    assert resp.json()["username"] == "admin"


def test_change_password(app_client, admin_token):
    resp = app_client.post("/auth/password", json={
        "current_password": "admin1234", "new_password": "newadmin1234",
    }, headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200

    resp = app_client.post("/auth/login", json={"username": "admin", "password": "newadmin1234"})
    assert resp.status_code == 200


def test_logout(app_client, admin_token):
    resp = app_client.post("/auth/logout", headers={"Authorization": f"Bearer {admin_token}"})
    assert resp.status_code == 200


def test_unauthorized_without_token(app_client):
    resp = app_client.get("/sql/tables")
    assert resp.status_code == 401


def test_sql_crud(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}

    resp = app_client.post("/sql/tables", json={
        "name": "products",
        "columns": [
            {"name": "id", "col_type": "INTEGER", "primary_key": True},
            {"name": "name", "col_type": "TEXT"},
        ],
    }, headers=h)
    assert resp.status_code == 200

    resp = app_client.post("/sql/tables/products/insert", json={
        "data": {"id": 1, "name": "Widget"},
    }, headers=h)
    assert resp.status_code == 200

    resp = app_client.get("/sql/tables/products", headers=h)
    assert resp.status_code == 200
    assert resp.json()["row_count"] == 1

    resp = app_client.get("/sql/tables", headers=h)
    assert resp.status_code == 200
    assert "products" in resp.json()["tables"]


def test_document_crud(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}

    resp = app_client.post(
        "/docs/logs", json={"data": {"event": "test", "level": "info"}}, headers=h
    )
    assert resp.status_code == 201
    doc_id = resp.json()["id"]

    resp = app_client.get(f"/docs/logs/{doc_id}", headers=h)
    assert resp.status_code == 200
    assert resp.json()["data"]["event"] == "test"

    resp = app_client.put(
        f"/docs/logs/{doc_id}",
        json={"data": {"level": "warn"}, "merge": True},
        headers=h,
    )
    assert resp.status_code == 200

    resp = app_client.delete(f"/docs/logs/{doc_id}", headers=h)
    assert resp.status_code == 200


def test_kv_crud(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}

    resp = app_client.put("/kv/config/theme", json={"value": "dark"}, headers=h)
    assert resp.status_code == 200

    resp = app_client.get("/kv/config/theme", headers=h)
    assert resp.status_code == 200
    assert resp.json()["value"] == "dark"

    resp = app_client.delete("/kv/config/theme", headers=h)
    assert resp.status_code == 200


def test_admin_stats(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    resp = app_client.get("/admin/stats", headers=h)
    assert resp.status_code == 200
    assert "tables" in resp.json()


def test_admin_audit(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    resp = app_client.get("/admin/audit", headers=h)
    assert resp.status_code == 200
    assert "logs" in resp.json()


def test_admin_audit_verify(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    resp = app_client.get("/admin/audit/verify", headers=h)
    assert resp.status_code == 200
    assert resp.json()["valid"] is True


def test_ebot_query(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}
    resp = app_client.post("/ebot/query", json={"text": "list tables"}, headers=h)
    assert resp.status_code == 200
    assert resp.json()["success"] is True


def test_graph_crud(app_client, admin_token):
    h = {"Authorization": f"Bearer {admin_token}"}

    resp = app_client.post(
        "/graph/nodes",
        json={"label": "Person", "properties": {"name": "Alice"}},
        headers=h,
    )
    assert resp.status_code == 201
    node_id = resp.json()["id"]

    resp = app_client.get(f"/graph/nodes/{node_id}", headers=h)
    assert resp.status_code == 200

    resp = app_client.post(
        "/graph/nodes",
        json={"label": "Person", "properties": {"name": "Bob"}},
        headers=h,
    )
    bob_id = resp.json()["id"]

    resp = app_client.post("/graph/edges", json={
        "source_id": node_id, "target_id": bob_id, "relationship": "KNOWS",
    }, headers=h)
    assert resp.status_code == 201

    resp = app_client.get("/graph/stats", headers=h)
    assert resp.json()["node_count"] == 2
    assert resp.json()["edge_count"] == 1


def test_rbac_read_only_cannot_write(app_client, admin_token):
    app_client.post("/auth/register", json={
        "username": "reader", "password": "readerpass123", "role": "read_only",
    })
    resp = app_client.post("/auth/login", json={"username": "reader", "password": "readerpass123"})
    reader_token = resp.json()["access_token"]
    rh = {"Authorization": f"Bearer {reader_token}"}

    resp = app_client.post("/sql/tables", json={
        "name": "forbidden", "columns": [{"name": "id", "col_type": "INTEGER"}],
    }, headers=rh)
    assert resp.status_code == 403
