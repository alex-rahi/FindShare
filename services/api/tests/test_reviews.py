def _login(client, username="demo_reviewer", password="FindShareDemo!dev"):
    response = client.post("/api/v1/auth/login", json={"email_or_username": username, "password": password})
    assert response.status_code == 200
    token = response.json()["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_categories_from_api(client):
    response = client.get("/api/v1/categories")
    slugs = [item["slug"] for item in response.json()]
    assert "technology" in slugs
    assert "fitness" in slugs
    fitness = next(item for item in response.json() if item["slug"] == "fitness")
    assert fitness["requires_health_notice"] is True
    assert fitness["subcategories"]


def test_feed_only_published(client):
    response = client.get("/api/v1/feed")
    titles = [item["title"] for item in response.json()["items"]]
    assert "Unfinished notes (draft)" not in titles
    assert "Quiet enough for a noisy office" in titles
    assert all(item["state"] == "published" for item in response.json()["items"])


def test_search_products_reviews_users(client):
    response = client.get("/api/v1/search", params={"q": "Quiet"})
    assert any(r["title"] == "Quiet enough for a noisy office" for r in response.json()["reviews"])
    products = client.get("/api/v1/search", params={"q": "yoga", "type": "product"})
    assert any("yoga" in p["name"].lower() for p in products.json()["products"])
    hidden = client.get("/api/v1/search", params={"q": "draft"})
    assert hidden.json()["reviews"] == []


def test_create_publish_and_hide_draft(client):
    headers = _login(client)
    products = client.get("/api/v1/products", params={"q": "skillet"})
    product_id = products.json()["items"][0]["id"]
    created = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "product_id": product_id,
            "title": "Solid daily pan",
            "body": "Demonstration text review for tests.",
            "overall_rating": 4,
            "pros": ["Heat retention"],
            "cons": ["Heavy"],
            "recommended": True,
            "review_kind": "personal",
        },
    )
    assert created.status_code == 201
    review_id = created.json()["id"]
    assert created.json()["state"] == "draft"
    feed = client.get("/api/v1/feed")
    assert review_id not in [item["id"] for item in feed.json()["items"]]
    published = client.post(f"/api/v1/reviews/{review_id}/publish", headers=headers)
    assert published.json()["state"] == "published"
    feed_after = client.get("/api/v1/feed")
    assert review_id in [item["id"] for item in feed_after.json()["items"]]


def test_cannot_edit_someone_elses_review(client):
    listing = client.get("/api/v1/reviews")
    skillet = next(item for item in listing.json()["items"] if "Even heat" in item["title"])
    headers = _login(client)
    response = client.patch(
        f"/api/v1/reviews/{skillet['id']}",
        headers=headers,
        json={"title": "Hijacked"},
    )
    assert response.status_code == 403


def test_draft_hidden_from_other_user(client):
    headers = _login(client, "admin", "FindShareAdmin!dev")
    products = client.get("/api/v1/products")
    created = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "product_id": products.json()["items"][0]["id"],
            "title": "Secret notes",
            "body": "Still drafting.",
            "overall_rating": 2,
        },
    )
    other = _login(client)
    hidden = client.get(f"/api/v1/reviews/{created.json()['id']}", headers=other)
    assert hidden.status_code == 404


def test_duplicate_product_rejected(client):
    headers = _login(client)
    categories = client.get("/api/v1/categories").json()
    outdoor = next(c for c in categories if c["slug"] == "outdoor-equipment")
    payload = {
        "name": "Trail Bottle 1L",
        "brand_name": "Trailform",
        "category_id": outdoor["id"],
        "description": "Demo bottle.",
    }
    assert client.post("/api/v1/products", headers=headers, json=payload).status_code == 201
    assert client.post("/api/v1/products", headers=headers, json=payload).status_code == 409


def test_profile_update(client):
    headers = _login(client)
    patched = client.patch(
        "/api/v1/profiles/me",
        headers=headers,
        json={"biography": "I review kitchen gear.", "interests": ["kitchen-products"]},
    )
    assert patched.status_code == 200
    assert patched.json()["profile"]["biography"] == "I review kitchen gear."
    public = client.get("/api/v1/users/demo_reviewer")
    assert all(item["state"] == "published" for item in public.json()["reviews"])
    assert "Unfinished notes (draft)" not in [i["title"] for i in public.json()["reviews"]]


def test_notices(client):
    response = client.get("/api/v1/meta/notices")
    assert response.json()["legal_review_required"] is True
    assert "does not independently guarantee" in response.json()["general"]


def test_cannot_edit_another_users_product(client):
    headers = _login(client)
    products = client.get("/api/v1/products").json()["items"]
    response = client.patch(
        f"/api/v1/products/{products[0]['id']}",
        headers=headers,
        json={"name": "Hijacked name"},
    )
    assert response.status_code == 403


def test_create_product_and_search(client):
    headers = _login(client)
    categories = client.get("/api/v1/categories").json()
    technology = next(item for item in categories if item["slug"] == "technology")
    name = "Test Gadget Alpha"
    created = client.post(
        "/api/v1/products",
        headers=headers,
        json={
            "name": name,
            "description": "Automated test product. Demonstration data.",
            "category_id": technology["id"],
            "brand_name": "FixtureBrand",
            "typical_price_min": 10,
            "typical_price_max": 20,
        },
    )
    assert created.status_code == 201, created.text
    found = client.get("/api/v1/search", params={"q": name, "type": "product"}).json()
    assert any(item["name"] == name for item in found["products"])


def test_publish_true_on_create(client):
    headers = _login(client)
    products = client.get("/api/v1/products").json()["items"]
    created = client.post(
        "/api/v1/reviews",
        headers=headers,
        json={
            "product_id": products[1]["id"],
            "title": "Published on create",
            "body": "Published demonstration review used by automated tests only. Extra text.",
            "overall_rating": 4,
            "pros": ["Test fixture"],
            "cons": ["Not a real purchase"],
            "recommended": True,
            "review_kind": "personal",
            "publish": True,
        },
    )
    assert created.status_code == 201, created.text
    assert created.json()["state"] == "published"
    feed_titles = [item["title"] for item in client.get("/api/v1/feed").json()["items"]]
    assert "Published on create" in feed_titles
