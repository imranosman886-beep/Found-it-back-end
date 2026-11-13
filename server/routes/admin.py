

from flask import Blueprint, request, jsonify


from flask import Blueprint, request, jsonify

from server.extensions import db
from server.models import User, LostItem, FoundItem
from server.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


# This route allows admins to view all registered users.

@admin_bp.route("/api/admin/users", methods=["GET"])
@admin_required
def get_users():
    users = User.query.order_by(User.id.desc()).all()

    return jsonify([
        {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
        for user in users
    ]), 200

# This route allows admins to change a user's role.

@admin_bp.route("/api/admin/users/<int:user_id>/role", methods=["PATCH"])
@admin_required
def update_user_role(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}
    role = data.get("role")

    if role not in ["student", "admin"]:
        return jsonify({"error": "Role must be student or admin"}), 400

    user.role = role
    db.session.commit()

    return jsonify({
        "message": "User role updated",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200



# ADMIN LOST AND FOUND ITEM MANAGEMENT
# This route allows admins to view all lost items.

@admin_bp.route("/api/admin/lost-items", methods=["GET"])
@admin_required
def admin_get_lost_items():
    items = LostItem.query.order_by(LostItem.id.desc()).all()

    return jsonify([
        {
            "id": item.id,
            "item_name": item.item_name,
            "description": item.description,
            "location": item.location,
            "date_lost": item.date_lost.isoformat(),
            "status": item.status,
            "user_id": item.user_id,
            "category_id": item.category_id
        }
        for item in items
    ]), 200


@admin_bp.route("/api/admin/found-items", methods=["GET"])
@admin_required
def admin_get_found_items():
    items = FoundItem.query.order_by(FoundItem.id.desc()).all()

    return jsonify([
        {
            "id": item.id,
            "item_name": item.item_name,
            "description": item.description,
            "location": item.location,
            "date_found": item.date_found.isoformat(),
            "status": item.status,
            "user_id": item.user_id,
            "category_id": item.category_id
        }
        for item in items
    ]), 200



@admin_bp.route("/api/admin/lost-items/<int:item_id>", methods=["PATCH"])
@admin_required
def admin_update_lost_item(item_id):
    item = db.session.get(LostItem, item_id)

    if not item:
        return jsonify({"error": "Lost item not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["open", "resolved"]:
        return jsonify({
            "error": "Status must be open or resolved"
        }), 400

    item.status = status
    db.session.commit()

    return jsonify({"message": "Lost item status updated"}), 200



# This route allows admins to update a found item's status.

@admin_bp.route("/api/admin/found-items/<int:item_id>", methods=["PATCH"])
@admin_required
def admin_update_found_item(item_id):
    item = db.session.get(FoundItem, item_id)

    if not item:
        return jsonify({"error": "Found item not found"}), 404

    data = request.get_json(silent=True) or {}
    status = data.get("status")

    if status not in ["available", "claimed", "returned"]:
        return jsonify({
            "error": "Status must be available, claimed or returned"
        }), 400

    item.status = status
    db.session.commit()

    return jsonify({"message": "Found item status updated"}), 200



# This route allows admins to delete lost items.

@admin_bp.route("/api/admin/lost-items/<int:item_id>", methods=["DELETE"])
@admin_required
def admin_delete_lost_item(item_id):
    item = db.session.get(LostItem, item_id)

    if not item:
        return jsonify({"error": "Lost item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Lost item deleted"}), 200



@admin_bp.route("/api/admin/found-items/<int:item_id>", methods=["DELETE"])
@admin_required
def admin_delete_found_item(item_id):
    item = db.session.get(FoundItem, item_id)

    if not item:
        return jsonify({"error": "Found item not found"}), 404

    if item.claims:
        return jsonify({
            "error": "Resolve or remove claims before deleting this item"
        }), 409

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Found item deleted"}), 200
