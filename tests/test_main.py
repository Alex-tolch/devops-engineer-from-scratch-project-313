from main import app


def test_ping_returns_pong():
    client = app.test_client()
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.data.decode() == "pong"


def test_list_links_empty():
    client = app.test_client()
    response = client.get("/api/links")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_link():
    client = app.test_client()
    response = client.post(
        "/api/links",
        json={"original_url": "https://example.com/long", "short_name": "ex"},
        content_type="application/json",
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["original_url"] == "https://example.com/long"
    assert data["short_name"] == "ex"
    assert data["short_url"] == "https://short.io/r/ex"
    assert "id" in data


def test_create_link_duplicate_short_name():
    client = app.test_client()
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/a", "short_name": "dup"},
        content_type="application/json",
    )
    response = client.post(
        "/api/links",
        json={"original_url": "https://example.com/b", "short_name": "dup"},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.get_json() == {"error": "short_name already exists"}


def test_list_links_returns_created():
    client = app.test_client()
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/one", "short_name": "one"},
        content_type="application/json",
    )
    response = client.get("/api/links")
    assert response.status_code == 200
    links = response.get_json()
    assert len(links) == 1
    assert links[0]["short_name"] == "one"
    assert links[0]["short_url"] == "https://short.io/r/one"


def test_get_link_by_id():
    client = app.test_client()
    create = client.post(
        "/api/links",
        json={"original_url": "https://example.com/get", "short_name": "get"},
        content_type="application/json",
    )
    link_id = create.get_json()["id"]
    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == link_id
    assert data["short_name"] == "get"


def test_get_link_404():
    client = app.test_client()
    response = client.get("/api/links/99999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}


def test_update_link():
    client = app.test_client()
    create = client.post(
        "/api/links",
        json={"original_url": "https://example.com/old", "short_name": "upd"},
        content_type="application/json",
    )
    link_id = create.get_json()["id"]
    response = client.put(
        f"/api/links/{link_id}",
        json={"original_url": "https://example.com/new", "short_name": "upd2"},
        content_type="application/json",
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["original_url"] == "https://example.com/new"
    assert data["short_name"] == "upd2"
    assert data["short_url"] == "https://short.io/r/upd2"


def test_update_link_404():
    client = app.test_client()
    response = client.put(
        "/api/links/99999",
        json={"original_url": "https://example.com/x", "short_name": "x"},
        content_type="application/json",
    )
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}


def test_update_link_duplicate_short_name():
    client = app.test_client()
    client.post(
        "/api/links",
        json={"original_url": "https://example.com/a", "short_name": "first"},
        content_type="application/json",
    )
    create2 = client.post(
        "/api/links",
        json={"original_url": "https://example.com/b", "short_name": "second"},
        content_type="application/json",
    )
    link_id = create2.get_json()["id"]
    response = client.put(
        f"/api/links/{link_id}",
        json={"original_url": "https://example.com/c", "short_name": "first"},
        content_type="application/json",
    )
    assert response.status_code == 422
    assert response.get_json() == {"error": "short_name already exists"}


def test_delete_link():
    client = app.test_client()
    create = client.post(
        "/api/links",
        json={"original_url": "https://example.com/del", "short_name": "del"},
        content_type="application/json",
    )
    link_id = create.get_json()["id"]
    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 204
    assert response.data == b""
    get_resp = client.get(f"/api/links/{link_id}")
    assert get_resp.status_code == 404


def test_delete_link_404():
    client = app.test_client()
    response = client.delete("/api/links/99999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Not Found"}
