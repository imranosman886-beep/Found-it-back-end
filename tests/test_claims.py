
def test_create_claim_without_login(client, found_item):
    response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone.",
        },
    )

    assert response.status_code == 401


def test_create_claim_success(
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

    response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone. I can identify the case.",
        },
    )

    assert response.status_code == 201


def test_cannot_claim_own_found_item(
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

    response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone.",
        },
    )

    # 403 means the user is forbidden from claiming
    # an item that they reported finding themselves.
    assert response.status_code == 403


def test_create_claim_missing_information(
    client,
    another_student,
):
    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/claims",
        json={"message": "This is my phone."},
    )

    assert response.status_code == 400


def test_cannot_claim_nonexistent_item(
    client,
    another_student,
):
    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        "/api/claims",
        json={
            "found_item_id": 9999,
            "message": "This is my phone.",
        },
    )

    assert response.status_code == 404


def test_duplicate_pending_claim_is_rejected(
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

    first_response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "I believe this is mine.",
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "I am submitting another claim.",
        },
    )

    # 409 means a pending claim already exists.
    assert second_response.status_code == 409


def test_get_my_claims(
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

    client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone.",
        },
    )

    response = client.get("/api/claims/my")

    assert response.status_code == 200
    assert response.get_json() is not None


def test_get_my_claims_requires_login(client):
    response = client.get("/api/claims/my")

    assert response.status_code == 401


def test_student_cannot_view_all_claims(
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

    response = client.get("/api/claims")

    assert response.status_code == 403


def test_admin_can_view_all_claims(
    client,
    admin,
):
    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.get("/api/claims")

    assert response.status_code == 200


def test_admin_can_approve_claim(
    client,
    admin,
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

    claim_response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "I can prove this phone belongs to me.",
        },
    )

    assert claim_response.status_code == 201

    claim_data = claim_response.get_json()
    claim = claim_data.get("claim", claim_data)
    claim_id = claim.get("id")

    assert claim_id is not None

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "approved"},
    )

    assert response.status_code == 200


def test_student_cannot_approve_claim(
    client,
    student,
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

    claim_response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone.",
        },
    )

    assert claim_response.status_code == 201

    claim_data = claim_response.get_json()
    claim = claim_data.get("claim", claim_data)
    claim_id = claim.get("id")

    assert claim_id is not None

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "approved"},
    )

    assert response.status_code == 403


def test_admin_cannot_use_invalid_claim_status(
    client,
    admin,
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

    claim_response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone.",
        },
    )

    assert claim_response.status_code == 201

    claim_data = claim_response.get_json()
    claim = claim_data.get("claim", claim_data)
    claim_id = claim.get("id")

    assert claim_id is not None

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "invalid-status"},
    )

    assert response.status_code == 400
