
from flask import Blueprint, request, jsonify, session

from server.extensions import db
from server.models import Claim, FoundItem, Notification
from server.utils.decorators import login_required, admin_required

claims_bp = Blueprint("claims", __name__)


def serialize_claim(claim):
    return {
        "id": claim.id,
        "message": claim.message,
        "status": claim.status,
        "user_id": claim.user_id,
        "found_item_id": claim.found_item_id
    }


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
        return jsonify({"error": "You cannot claim your own item"}), 403

    if found_item.status != "available":
        return jsonify({"error": "This item is not available for claims"}), 409

    existing_claim = Claim.query.filter_by(
        user_id=user_id,
        found_item_id=found_item_id,
        status="pending"
    ).first()

    if existing_claim:
        return jsonify({"error": "You already have a pending claim"}), 409

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
    claims = Claim.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Claim.id.desc()).all()

    return jsonify([serialize_claim(claim) for claim in claims]), 200


@claims_bp.route("/api/claims", methods=["GET"])
@admin_required
def get_all_claims():
    claims = Claim.query.order_by(Claim.id.desc()).all()

    return jsonify([serialize_claim(claim) for claim in claims]), 200


@claims_bp.route("/api/claims/<int:claim_id>", methods=["PATCH"])
@admin_required
def update_claim(claim_id):
    claim = db.session.get(Claim, claim_id)

    if not claim:
        return jsonify({"error": "Claim not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["pending", "approved", "rejected"]:
        return jsonify({
            "error": "Status must be pending, approved or rejected"
        }), 400

    if status == "approved" and claim.found_item.status != "available":
        return jsonify({"error": "This item is no longer available"}), 409

    claim.status = status

    if status == "approved":
        claim.found_item.status = "claimed"

        # Reject other pending claims for the same item.
        other_claims = Claim.query.filter(
            Claim.found_item_id == claim.found_item_id,
            Claim.id != claim.id,
            Claim.status == "pending"
        ).all()

        for other in other_claims:
            other.status = "rejected"

    notification = Notification(
        message=f"Your claim has been {status}.",
        user_id=claim.user_id
    )

    db.session.add(notification)
    db.session.commit()

    return jsonify({
        "message": "Claim updated",
        "claim": serialize_claim(claim)
    }), 200
