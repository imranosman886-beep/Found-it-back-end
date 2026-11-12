
def test_signup_success(client):
    response = client.post(
        "/signup",
        json={
            "email": "newstudent@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201


def test_signup_missing_information(client):
    response = client.post(
        "/signup",
        json={
            "email": "newstudent@test.com",
        },
    )

    assert response.status_code == 400


def test_signup_short_password(client):
    response = client.post(
        "/signup",
        json={
            "email": "newstudent@test.com",
            "password": "short",
        },
    )

    assert response.status_code == 400


def test_signup_duplicate_email(client, student):
    response = client.post(
        "/signup",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 409


def test_signup_creates_student_role(client, app):
    response = client.post(
        "/signup",
        json={
            "email": "newstudent@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 201

    from server.models import User

    with app.app_context():
        user = User.query.filter_by(
            email="newstudent@test.com"
        ).first()

        assert user is not None
        assert user.role == "student"


def test_login_success(client, student):
    response = client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200


def test_login_wrong_password(client, student):
    response = client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_login_unknown_user(client):
    response = client.post(
        "/login",
        json={
            "email": "unknown@test.com",
            "password": "password123",
        },
    )

    assert response.status_code == 401


def test_check_session_without_login(client):
    response = client.get("/check_session")

    assert response.status_code == 200

    data = response.get_json()
    assert data["logged_in"] is False


def test_check_session_after_login(client, student):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.get("/check_session")

    assert response.status_code == 200

    data = response.get_json()
    assert data["logged_in"] is True


def test_logout(client, student):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.delete("/logout")

    assert response.status_code == 200

    session_response = client.get("/check_session")
    assert session_response.get_json()["logged_in"] is False
