
def test_get_categories(client, category):
    response = client.get("/api/categories")

    assert response.status_code == 200
    assert response.get_json() is not None


def test_create_category_as_admin(client, admin):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.post(
        "/api/categories",
        json={"name": "Clothing"},
    )

    assert response.status_code in (200, 201)


def test_create_category_without_login(client):
    response = client.post(
        "/api/categories",
        json={"name": "Clothing"},
    )

    assert response.status_code == 401


def test_create_category_as_student(client, student):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/categories",
        json={"name": "Clothing"},
    )

    assert response.status_code == 403


def test_delete_category_as_admin(client, admin, category):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.delete(
        f"/api/categories/{category}"
    )

    assert response.status_code == 200


def test_delete_category_without_login(client, category):
    response = client.delete(
        f"/api/categories/{category}"
    )

    assert response.status_code == 401


def test_cannot_delete_category_with_items(
    client,
    admin,
    category,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.delete(
        f"/api/categories/{category}"
    )

    # 409 means the category cannot be deleted
    # because other records are still using it.
    assert response.status_code == 409

