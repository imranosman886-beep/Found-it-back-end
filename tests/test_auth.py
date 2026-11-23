
def test_signup_success(client, approved_student_credential):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": "student.test@moringaschool.com",
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "student",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "student"


def test_staff_signup_success(client, approved_staff_credential):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Staff",
            "email": "staff.test@moringaschool.com",
            "institutional_id": "MOR-STF-TEST",
            "university_code": "MOR",
            "account_type": "staff",
            "password": "password123",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["user"]["role"] == "staff"


def test_signup_missing_information(client):
    response = client.post(
        "/signup",
        json={
            "email": "student.test@moringaschool.com",
            "password": "password123",
        },
    )

    assert response.status_code == 400


def test_signup_short_password(client, approved_student_credential):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": "student.test@moringaschool.com",
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "student",
            "password": "short",
        },
    )

    assert response.status_code == 400


def test_signup_unapproved_id(client, university):
    response = client.post(
        "/signup",
        json={
            "full_name": "Unknown Student",
            "email": "unknown@moringaschool.com",
            "institutional_id": "MOR-STU-999",
            "university_code": "MOR",
            "account_type": "student",
            "password": "password123",
        },
    )

    assert response.status_code == 403
    assert response.json["error"] == "Institutional ID is not approved"


def test_signup_wrong_email(client, approved_student_credential):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": "wrong@moringaschool.com",
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "student",
            "password": "password123",
        },
    )

    assert response.status_code == 403


def test_signup_wrong_account_type(client, approved_student_credential):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": "student.test@moringaschool.com",
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "staff",
            "password": "password123",
        },
    )

    assert response.status_code == 403


def test_signup_duplicate_credential(
    client,
    approved_student_credential,
):
    registration_data = {
        "full_name": "Test Student",
        "email": "student.test@moringaschool.com",
        "institutional_id": "MOR-STU-TEST",
        "university_code": "MOR",
        "account_type": "student",
        "password": "password123",
    }

    first_response = client.post(
        "/signup",
        json=registration_data,
    )

    second_response = client.post(
        "/signup",
        json=registration_data,
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 409


def test_signup_rejects_admin_account(client):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Admin",
            "email": "admin@moringaschool.com",
            "institutional_id": "MOR-ADMIN-001",
            "university_code": "MOR",
            "account_type": "admin",
            "password": "password123",
        },
    )

    assert response.status_code == 400


def test_login_success(
    client,
    approved_student_credential,
):
    client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": "student.test@moringaschool.com",
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "student",
            "password": "password123",
        },
    )

    response = client.post(
        "/login",
        json={
            "institutional_id": "MOR-STU-TEST",
            "password": "password123",
        },
    )

    assert response.status_code == 200


def test_login_wrong_password(
    client,
    approved_student_credential,
):
    client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": "student.test@moringaschool.com",
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "student",
            "password": "password123",
        },
    )

    response = client.post(
        "/login",
        json={
            "institutional_id": "MOR-STU-TEST",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


def test_login_unknown_id(client):
    response = client.post(
        "/login",
        json={
            "institutional_id": "MOR-STU-999",
            "password": "password123",
        },
    )

    assert response.status_code == 401


def test_login_rejects_non_string_id(client):
    response = client.post(
        "/login",
        json={
            "institutional_id": 123,
            "password": "password123",
        },
    )

    assert response.status_code == 400


def test_check_session_without_login(client):
    response = client.get("/check_session")

    assert response.status_code == 200
    assert response.get_json()["logged_in"] is False


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
    assert response.get_json()["logged_in"] is True


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


def test_signup_rejects_non_object_json(client):
    response = client.post(
        "/signup",
        json=["student@moringaschool.com", "password123"],
    )

    assert response.status_code == 400


def test_signup_rejects_non_string_email(client):
    response = client.post(
        "/signup",
        json={
            "full_name": "Test Student",
            "email": 123,
            "institutional_id": "MOR-STU-TEST",
            "university_code": "MOR",
            "account_type": "student",
            "password": "password123",
        },
    )

    assert response.status_code == 400


def test_login_rejects_non_object_json(client):
    response = client.post(
        "/login",
        json=["MOR-STU-TEST", "password123"],
    )

    assert response.status_code == 400


def test_login_rejects_non_string_password(client):
    response = client.post(
        "/login",
        json={
            "institutional_id": "MOR-STU-TEST",
            "password": 123,
        },
    )

    assert response.status_code == 400
