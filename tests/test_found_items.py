
def test_get_found_items(client, found_item):
    response = client.get("/api/found-items")

    assert response.status_code == 200
    assert response.get_json() is not None


def test_get_single_found_item(client, found_item):
    response = client.get(
        f"/api/found-items/{found_item}"
    )

    assert response.status_code == 200


def test_get_missing_found_item(client):
    response = client.get("/api/found-items/9999")

    assert response.status_code == 404


def test_create_found_item_without_login(client, category):
    response = client.post(
        "/api/found-items",
        json={
            "item_name": "Found Wallet",
            "description": "Brown leather wallet",
            "location": "Reception",
            "date_found": "2026-11-05",
            "category_id": category,
        },
    )

    assert response.status_code == 401


def test_create_found_item(client, student, category):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/found-items",
        json={
            "item_name": "Found Wallet",
            "description": "Brown leather wallet",
            "location": "Reception",
            "date_found": "2026-11-05",
            "category_id": category,
        },
    )

    assert response.status_code == 201


def test_create_found_item_missing_fields(
    client,
    student,
):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/found-items",
        json={"item_name": "Found Wallet"},
    )

    assert response.status_code == 400


def test_update_own_found_item(
    client,
    student,
    found_item,
):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/found-items/{found_item}",
        json={"item_name": "Updated Phone"},
    )

    assert response.status_code == 200


def test_another_user_cannot_update_found_item(
    client,
    another_student,
    found_item,
):
    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/found-items/{found_item}",
        json={"item_name": "Changed by another user"},
    )

    assert response.status_code == 403


def test_delete_own_found_item(
    client,
    student,
    found_item,
):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.delete(
        f"/api/found-items/{found_item}"
    )

    assert response.status_code == 200


def test_another_user_cannot_delete_found_item(
    client,
    another_student,
    found_item,
):
    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.delete(
        f"/api/found-items/{found_item}"
    )

    assert response.status_code == 403
