
from server.models import Notification
from server.extensions import db


def test_get_notifications_requires_login(client):
    response = client.get("/api/notifications")

    assert response.status_code == 401


def test_student_can_get_own_notifications(
    client,
    app,
    student,
):
    with app.app_context():
        notification = Notification(
            message="Someone submitted a claim on your item.",
            user_id=student,
        )

        db.session.add(notification)
        db.session.commit()

    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.get("/api/notifications")

    assert response.status_code == 200
    assert response.get_json() is not None


def test_student_can_mark_own_notification_as_read(
    client,
    app,
    student,
):
    with app.app_context():
        notification = Notification(
            message="Your item has received a claim.",
            user_id=student,
        )

        db.session.add(notification)
        db.session.commit()

        notification_id = notification.id

    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/notifications/{notification_id}/read"
    )

    assert response.status_code == 200


def test_student_cannot_mark_another_users_notification_as_read(
    client,
    app,
    another_student,
    student,
):
    with app.app_context():
        notification = Notification(
            message="This belongs to another student.",
            user_id=another_student,
        )

        db.session.add(notification)
        db.session.commit()

        notification_id = notification.id

    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/notifications/{notification_id}/read"
    )

    assert response.status_code == 403


def test_mark_missing_notification_as_read(client, student):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        "/api/notifications/9999/read"
    )

    assert response.status_code == 404
