
from server.models import User, LostItem, FoundItem
from server.extensions import db


# Checks that users must log in before accessing admin routes
def test_admin_users_requires_login(client):
    response = client.get("/api/admin/users")

    assert response.status_code == 401


# Checks that a normal student cannot access the admin users page
def test_student_cannot_access_admin_users(
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

    response = client.get("/api/admin/users")

    assert response.status_code == 403


# Checks that an admin can view all registered users
def test_admin_can_view_users(client, admin):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.get("/api/admin/users")

    assert response.status_code == 200


# Checks that an admin can change a student's role
def test_admin_can_change_user_role(
    client,
    admin,
    student,
    app,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/admin/users/{student}/role",
        json={"role": "admin"},
    )

    assert response.status_code == 200

    # Confirms that the user's role was updated in the database
    with app.app_context():
        user = db.session.get(User, student)

        assert user.role == "admin"


# Checks that an admin cannot assign a role that does not exist
def test_admin_cannot_assign_invalid_role(
    client,
    admin,
    student,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/admin/users/{student}/role",
        json={"role": "superuser"},
    )

    assert response.status_code == 400


# Checks that an admin can view all reported lost items
def test_admin_can_view_lost_items(
    client,
    admin,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.get("/api/admin/lost-items")

    assert response.status_code == 200


# Checks that an admin can view all reported found items
def test_admin_can_view_found_items(
    client,
    admin,
    found_item,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.get("/api/admin/found-items")

    assert response.status_code == 200


# Checks that an admin can update the status of a lost item
def test_admin_can_update_lost_item_status(
    client,
    admin,
    lost_item,
    app,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/admin/lost-items/{lost_item}",
        json={"status": "resolved"},
    )

    assert response.status_code == 200

    # Confirms that the new status was saved in the database
    with app.app_context():
        item = db.session.get(LostItem, lost_item)

        assert item.status == "resolved"


# Checks that an admin can update the status of a found item
def test_admin_can_update_found_item_status(
    client,
    admin,
    found_item,
    app,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/admin/found-items/{found_item}",
        json={"status": "returned"},
    )

    assert response.status_code == 200

    # Confirms that the new status was saved in the database
    with app.app_context():
        item = db.session.get(FoundItem, found_item)

        assert item.status == "returned"


# Checks that an admin cannot use an invalid status for a lost item
def test_admin_cannot_set_invalid_lost_item_status(
    client,
    admin,
    lost_item,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/admin/lost-items/{lost_item}",
        json={"status": "invalid"},
    )

    assert response.status_code == 400


# Checks that an admin cannot use an invalid status for a found item
def test_admin_cannot_set_invalid_found_item_status(
    client,
    admin,
    found_item,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/admin/found-items/{found_item}",
        json={"status": "invalid"},
    )

    assert response.status_code == 400


# Checks that a normal student cannot update an item's status
def test_student_cannot_update_admin_item_status(
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
        f"/api/admin/lost-items/{lost_item}",
        json={"status": "resolved"},
    )

    assert response.status_code == 403
