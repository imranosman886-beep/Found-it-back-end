
from datetime import datetime

from flask import Blueprint, request, jsonify, session

from server.extensions import db
from server.models import Claim, FoundItem, Notification, User
from server.utils.decorators import login_required, admin_required


claims_bp = Blueprint("claims", __name__)


def serialize_claim(claim):
    return {
        "id": claim.id,
        "message": claim.message,
        "status": claim.status,
        "user_id": claim.user_id,
        "found_item_id": claim.found_item_id,
        "handover_completed": claim.found_item.handover_completed,
        "handover_completed_at": (
            claim.found_item.handover_completed_at.isoformat()
            if claim.found_item.handover_completed_at
            else None
        ),
    }


def can_manage_claim():
    user = db.session.get(User, session["user_id"])
    return user is not None and user.role == "admin"


@claims_bp.route("/api/claims", methods=["POST"])
@login_required
def create_claim():
    """
    Submit a claim for a found item.
    ---
    tags:
      - Claims
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - message
            - found_item_id
          properties:
            message:
              type: string
              example: This is my phone. It has a small scratch on the back.
            found_item_id:
              type: integer
              example: 1
    responses:
      201:
        description: Claim submitted successfully
      400:
        description: Missing or invalid information
      403:
        description: Cannot claim your own item
      404:
        description: Found item not found
      409:
        description: Item unavailable or pending claim already exists
    """
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()
    found_item_id = data.get("found_item_id")

    if not message or not found_item_id:
        return jsonify({
            "error": "Message and found_item_id are required"
        }), 400

    try:
        found_item_id = int(found_item_id)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid found_item_id"}), 400

    found_item = db.session.get(FoundItem, found_item_id)

    if not found_item:
        return jsonify({"error": "Found item not found"}), 404

    user_id = session["user_id"]

    if found_item.user_id == user_id:
        return jsonify({
            "error": "You cannot claim your own item"
        }), 403

    if found_item.status != "available":
        return jsonify({
            "error": "This item is not available for claims"
        }), 409

    existing_claim = Claim.query.filter_by(
        user_id=user_id,
        found_item_id=found_item_id,
        status="pending"
    ).first()

    if existing_claim:
        return jsonify({
            "error": "You already have a pending claim"
        }), 409

    claim = Claim(
        message=message,
        user_id=user_id,
        found_item_id=found_item_id
    )

    notification = Notification(
        message="Someone has submitted a claim for your found item.",
        user_id=found_item.user_id
    )

    db.session.add(claim)
    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Claim submitted successfully",
        "claim": serialize_claim(claim)
    }), 201


@claims_bp.route("/api/claims/my", methods=["GET"])
@login_required
def get_my_claims():
    """
    Get your submitted claims.
    ---
    tags:
      - Claims
    responses:
      200:
        description: List of your claims
    """
    claims = Claim.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Claim.id.desc()).all()

    return jsonify([
        serialize_claim(claim) for claim in claims
    ]), 200


@claims_bp.route("/api/claims", methods=["GET"])
@admin_required
def get_all_claims():
    """
    Get all claims (admin only).
    ---
    tags:
      - Claims
    responses:
      200:
        description: List of all claims
    """
    claims = Claim.query.order_by(Claim.id.desc()).all()

    return jsonify([
        serialize_claim(claim) for claim in claims
    ]), 200


@claims_bp.route("/api/claims/<int:claim_id>", methods=["PATCH"])
@login_required
def update_claim(claim_id):
    """
    Approve or reject a claim (admin only).
    ---
    tags:
      - Claims
    parameters:
      - name: claim_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - status
          properties:
            status:
              type: string
              enum:
                - approved
                - rejected
              example: approved
    responses:
      200:
        description: Claim updated successfully
      400:
        description: Invalid status
      403:
        description: Not authorized
      404:
        description: Claim not found
      409:
        description: Claim already decided or item unavailable
    """
    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"error": "Claim not found"}), 404

    if not can_manage_claim():
        return jsonify({
            "error": "You are not authorized to manage this claim"
        }), 403

    if claim.status != "pending":
        return jsonify({
            "error": "This claim has already been decided"
        }), 409

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["approved", "rejected"]:
        return jsonify({
            "error": "Status must be approved or rejected"
        }), 400

    found_item = claim.found_item

    if status == "approved":
        if found_item.status != "available":
            return jsonify({
                "error": "This item is no longer available"
            }), 409

        found_item.status = "claimed"

        other_claims = Claim.query.filter(
            Claim.found_item_id == found_item.id,
            Claim.id != claim.id,
            Claim.status == "pending"
        ).all()

        for other in other_claims:
            other.status = "rejected"

            db.session.add(Notification(
                message="Your claim was rejected because another claim was approved.",
                user_id=other.user_id
            ))

    claim.status = status

    db.session.add(Notification(
        message=f"Your claim has been {status}.",
        user_id=claim.user_id
    ))

    db.session.commit()

    return jsonify({
        "message": "Claim updated successfully",
        "claim": serialize_claim(claim)
    }), 200


@claims_bp.route(
    "/api/claims/<int:claim_id>/handover",
    methods=["POST"]
)
@login_required
def complete_handover(claim_id):
    """
    Record a completed item handover (admin only).
    ---
    tags:
      - Claims
    parameters:
      - name: claim_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Handover completed successfully
      403:
        description: Not authorized
      404:
        description: Claim not found
      409:
        description: Claim is not approved or handover already completed
    """
    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"error": "Claim not found"}), 404

    if not can_manage_claim():
        return jsonify({
            "error": "You are not authorized to record this handover"
        }), 403

    if claim.status != "approved":
        return jsonify({
            "error": "Only approved claims can be handed over"
        }), 409

    found_item = claim.found_item

    if found_item.handover_completed:
        return jsonify({
            "error": "Handover has already been completed"
        }), 409

    found_item.handover_completed = True
    found_item.handover_completed_at = datetime.utcnow()

    db.session.add(Notification(
        message="Your claimed item has been marked as handed over.",
        user_id=claim.user_id
    ))

    db.session.commit()

    return jsonify({
        "message": "Handover completed successfully",
        "claim": serialize_claim(claim)
    }), 200
