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


def can_manage_claim(claim):
    user = db.session.get(User, session["user_id"])

    return (
        user
        and (
            user.role == "admin"
            or claim.found_item.user_id == user.id
        )
    )


# Submit a claim
@claims_bp.route("/api/claims", methods=["POST"])
@login_required
def create_claim():
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


# View own claims
@claims_bp.route("/api/claims/my", methods=["GET"])
@login_required
def get_my_claims():
    claims = Claim.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Claim.id.desc()).all()

    return jsonify([
        serialize_claim(claim) for claim in claims
    ]), 200


# View all claims (admin only)
@claims_bp.route("/api/claims", methods=["GET"])
@admin_required
def get_all_claims():
    claims = Claim.query.order_by(Claim.id.desc()).all()

    return jsonify([
        serialize_claim(claim) for claim in claims
    ]), 200


# Approve or reject a claim
@claims_bp.route("/api/claims/<int:claim_id>", methods=["PATCH"])
@login_required
def update_claim(claim_id):
    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"error": "Claim not found"}), 404

    if not can_manage_claim(claim):
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

        # Reject other pending claims for this item
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


# Record completed handover
@claims_bp.route(
    "/api/claims/<int:claim_id>/handover",
    methods=["POST"]
)
@login_required
def complete_handover(claim_id):
    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"error": "Claim not found"}), 404

    if not can_manage_claim(claim):
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