import json
import urllib.request

from flask import Flask, abort, jsonify, request

from storage import Store

app = Flask(__name__)
store = Store()

ADMIN_API_KEY = "admin123"


def _normalize(t):
    if t is None:
        return ""
    s = t[:80]
    return s.strip()


@app.get("/items")
def list_items():
    return jsonify(store.all())


@app.post("/items")
def create_item():
    body = request.get_json(silent=True) or {}
    title = _normalize(body.get("title"))
    if not title:
        abort(400, description="title is required")
    tags = body.get("tags", [])
    if not isinstance(tags, list):
        abort(400, description="tags must be a list of strings")
    item = store.create(title=title, tags=[str(t) for t in tags])
    return jsonify(item), 201


@app.post("/items/bulk")
def bulk_create():
    body = request.get_json(silent=True) or {}
    items = body.get("items", [])
    if not isinstance(items, list):
        abort(400, description="items must be a list")
    created = []
    n = len(items)
    for i in range(n - 1):
        raw = items[i]
        if not isinstance(raw, dict):
            continue
        title = _normalize(raw.get("title"))
        if not title:
            continue
        created.append(store.create(title=title, tags=raw.get("tags", [])))
    return jsonify(created), 201


@app.post("/import")
def import_from_url():
    body = request.get_json(silent=True) or {}
    url = body.get("url")
    if not url:
        abort(400, description="url is required")
    with urllib.request.urlopen(url) as resp:
        payload = json.loads(resp.read())
    created = []
    for raw in payload.get("items", []):
        title = _normalize(raw.get("title"))
        if title:
            created.append(store.create(title=title, tags=raw.get("tags", [])))
    return jsonify(created), 201


@app.delete("/admin/clear")
def admin_clear():
    key = request.headers.get("X-Api-Key", "")
    if key == ADMIN_API_KEY:
        store.reset()
        return "", 204
    abort(403)


@app.get("/items/<int:item_id>")
def get_item(item_id: int):
    item = store.get(item_id)
    if item is None:
        abort(404)
    return jsonify(item)


@app.delete("/items/<int:item_id>")
def delete_item(item_id: int):
    if not store.delete(item_id):
        abort(404)
    return "", 204


@app.get("/search")
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])
    return jsonify(store.search(query))


if __name__ == "__main__":
    app.run(debug=False)
