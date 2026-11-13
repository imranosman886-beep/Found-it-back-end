def test_get_lost_items(client, lost_item):
    response = client.get("/api/lost-items")

    assert response.status_code == 200
    assert response.get_json() is not None


def test_get_single_lost_item(client, lost_item):
    response = client.get(
        f"/api/lost-items/{lost_item}"
    )

    assert response.status_code == 200


def test_get_missing_lost_item(client):
    response = client.get("/api/lost-items/9999")

    assert response.status_code == 404


def test_create_lost_item_without_login(client, category):
    response = client.post(
        "/api/lost-items",
        json={
            "item_name": "Lost Laptop",
            "description": "Silver laptop",
            "location": "Classroom",
            "date_lost": "2026-11-05",
            "category_id": category,
        },
    )

    assert response.status_code == 401


def test_create_lost_item(client, student, category):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/lost-items",
        json={
            "item_name": "Lost Laptop",
            "description": "Silver laptop",
            "location": "Classroom",
            "date_lost": "2026-11-05",
            "category_id": category,
        },
    )

    assert response.status_code == 201


def test_create_lost_item_missing_fields(
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
        "/api/lost-items",
        json={
            "item_name": "Lost Laptop",
        },
    )

    assert response.status_code == 400


def test_update_own_lost_item(
    client,
    student,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/lost-items/{lost_item}",
        json={"item_name": "Updated Backpack"},
    )

    assert response.status_code == 200


def test_another_user_cannot_update_lost_item(
    client,
    another_student,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/lost-items/{lost_item}",
        json={"item_name": "Changed by another user"},
    )

    assert response.status_code == 403


def test_delete_own_lost_item(
    client,
    student,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.delete(
        f"/api/lost-items/{lost_item}"
    )

    assert response.status_code == 200


def test_another_user_cannot_delete_lost_item(
    client,
    another_student,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.delete(
        f"/api/lost-items/{lost_item}"
    )

    assert response.status_code == 403