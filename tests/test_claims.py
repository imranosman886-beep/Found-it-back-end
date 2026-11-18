
from server.models import Notification


def test_create_claim_without_login(client, found_item):
    response = client.post(
        "/api/claims",
        json={
            "found_item_id": found_item,
            "message": "This is my phone.",
        },
    )

    assert response.status_code == 401


def test_create_claim_success(client, another_student, found_item):
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


def test_cannot_claim_own_found_item(client, student, found_item):
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

    assert response.status_code == 403


def test_create_claim_missing_information(client, another_student):
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


def test_cannot_claim_nonexistent_item(client, another_student):
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

    assert second_response.status_code == 409


def test_get_my_claims(client, another_student, found_item):
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


def test_student_cannot_view_all_claims(client, student):
    client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )

    response = client.get("/api/claims")

    assert response.status_code == 403


def test_admin_can_view_all_claims(client, admin):
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

    claim_id = claim_response.get_json()["claim"]["id"]

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
    assert response.get_json()["claim"]["status"] == "approved"


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

    claim_id = claim_response.get_json()["claim"]["id"]

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

    claim_id = claim_response.get_json()["claim"]["id"]

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


# Additional claims tests


def test_admin_can_reject_claim(
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

    claim_id = claim_response.get_json()["claim"]["id"]

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
        json={"status": "rejected"},
    )

    assert response.status_code == 200
    assert response.get_json()["claim"]["status"] == "rejected"


def test_admin_cannot_decide_claim_twice(
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

    claim_id = claim_response.get_json()["claim"]["id"]

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "rejected"},
    )

    response = client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "approved"},
    )

    assert response.status_code == 409


def test_admin_can_complete_handover(
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

    claim_id = claim_response.get_json()["claim"]["id"]

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    approval = client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "approved"},
    )

    assert approval.status_code == 200

    response = client.post(
        f"/api/claims/{claim_id}/handover"
    )

    assert response.status_code == 200

    claim_data = response.get_json()["claim"]

    assert claim_data["handover_completed"] is True
    assert claim_data["handover_completed_at"] is not None


def test_student_cannot_complete_handover(
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

    claim_id = claim_response.get_json()["claim"]["id"]

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "approved"},
    )

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "another@test.com",
            "password": "password123",
        },
    )

    response = client.post(
        f"/api/claims/{claim_id}/handover"
    )

    assert response.status_code == 403


def test_cannot_complete_handover_twice(
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

    claim_id = claim_response.get_json()["claim"]["id"]

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    client.patch(
        f"/api/claims/{claim_id}",
        json={"status": "approved"},
    )

    first_response = client.post(
        f"/api/claims/{claim_id}/handover"
    )

    second_response = client.post(
        f"/api/claims/{claim_id}/handover"
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 409


def test_cannot_complete_handover_before_approval(
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

    claim_id = claim_response.get_json()["claim"]["id"]

    client.delete("/logout")

    client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )

    response = client.post(
        f"/api/claims/{claim_id}/handover"
    )

    assert response.status_code == 409


def test_claim_submission_notifies_item_owner(
    client,
    another_student,
    student,
    found_item,
    app,
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
            "message": "This is my phone.",
        },
    )

    assert response.status_code == 201

    with app.app_context():
        notification = Notification.query.filter_by(
            user_id=student
        ).first()

        assert notification is not None
        assert "claim" in notification.message.lower()


def test_approved_claim_notifies_claimant(
    client,
    admin,
    another_student,
    found_item,
    app,
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

    claim_id = claim_response.get_json()["claim"]["id"]

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

    with app.app_context():
        notification = Notification.query.filter_by(
            user_id=another_student
        ).first()

        assert notification is not None
        assert "approved" in notification.message.lower()
