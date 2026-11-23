
from flask import Blueprint, request, jsonify

from server.extensions import db
from server.models import User, LostItem, FoundItem
from server.utils.decorators import admin_required

admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/api/admin/users", methods=["GET"])
@admin_required
def get_users():
    """
    Get all users (admin only).
    ---
    tags:
      - Administration
    responses:
      200:
        description: List of users
    """
    users = User.query.order_by(User.id.desc()).all()

    return jsonify([
        {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "institutional_id": user.institutional_id,
            "role": user.role,
            "university": user.university.name if user.university else None
        }
        for user in users
    ]), 200


@admin_bp.route("/api/admin/users/<int:user_id>/role", methods=["PATCH"])
@admin_required
def update_user_role(user_id):
    """
    Update a user's role (admin only).
    ---
    tags:
      - Administration
    parameters:
      - name: user_id
        in: path
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - role
          properties:
            role:
              type: string
              enum:
                - student
                - staff
                - admin
    responses:
      200:
        description: User role updated
      400:
        description: Invalid role
      404:
        description: User not found
    """
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Request body must be a JSON object"}), 400

    role = data.get("role")

    if role not in ["student", "staff", "admin"]:
        return jsonify({
            "error": "Role must be student, staff or admin"
        }), 400

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


@admin_bp.route("/api/admin/lost-items", methods=["GET"])
@admin_required
def admin_get_lost_items():
    """
    Get all lost item reports (admin only).
    ---
    tags:
      - Administration
    responses:
      200:
        description: List of lost items
    """
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
    """
    Get all found item reports (admin only).
    ---
    tags:
      - Administration
    responses:
      200:
        description: List of found items
    """
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
    """
    Update lost item status (admin only).
    ---
    tags:
      - Administration
    parameters:
      - name: item_id
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
                - open
                - resolved
    responses:
      200:
        description: Lost item status updated
      400:
        description: Invalid status
      404:
        description: Lost item not found
    """
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


@admin_bp.route("/api/admin/found-items/<int:item_id>", methods=["PATCH"])
@admin_required
def admin_update_found_item(item_id):
    """
    Update found item status (admin only).
    ---
    tags:
      - Administration
    parameters:
      - name: item_id
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
                - available
                - claimed
                - returned
    responses:
      200:
        description: Found item status updated
      400:
        description: Invalid status
      404:
        description: Found item not found
    """
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


@admin_bp.route("/api/admin/lost-items/<int:item_id>", methods=["DELETE"])
@admin_required
def admin_delete_lost_item(item_id):
    """
    Delete a lost item report (admin only).
    ---
    tags:
      - Administration
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lost item deleted
      404:
        description: Lost item not found
    """
    item = db.session.get(LostItem, item_id)

    if not item:
        return jsonify({"error": "Lost item not found"}), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Lost item deleted"}), 200


@admin_bp.route("/api/admin/found-items/<int:item_id>", methods=["DELETE"])
@admin_required
def admin_delete_found_item(item_id):
    """
    Delete a found item report (admin only).
    ---
    tags:
      - Administration
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Found item deleted
      404:
        description: Found item not found
      409:
        description: Item has unresolved claims
    """
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
