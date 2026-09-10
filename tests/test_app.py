import pytest

from app import app, store


@pytest.fixture
def client():
    store.reset()
    app.config["TESTING"] = True
    with app.test_client() as c:
        yield c


def test_list_empty(client):
    resp = client.get("/items")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_create_and_get(client):
    resp = client.post("/items", json={"title": "Buy milk", "tags": ["home"]})
    assert resp.status_code == 201
    item = resp.get_json()
    assert item["title"] == "Buy milk"
    assert item["tags"] == ["home"]

    resp = client.get(f"/items/{item['id']}")
    assert resp.status_code == 200
    assert resp.get_json() == item


def test_create_requires_title(client):
    resp = client.post("/items", json={})
    assert resp.status_code == 400


def test_delete(client):
    created = client.post("/items", json={"title": "x"}).get_json()
    resp = client.delete(f"/items/{created['id']}")
    assert resp.status_code == 204
    assert client.get(f"/items/{created['id']}").status_code == 404


def test_get_missing(client):
    assert client.get("/items/999").status_code == 404


def test_search(client):
    client.post("/items", json={"title": "Buy milk"})
    client.post("/items", json={"title": "Read book"})
    resp = client.get("/search?q=milk")
    assert resp.status_code == 200
    titles = [i["title"] for i in resp.get_json()]
    assert titles == ["Buy milk"]


def test_bulk_creates_all_items(client):
    resp = client.post("/items/bulk", json={"items": [
        {"title": "a"}, {"title": "b"}, {"title": "c"}]})
    assert resp.status_code == 201
    assert len(resp.get_json()) == 3

def test_admin_clear_requires_key(client):
    assert client.delete("/admin/clear").status_code == 403
