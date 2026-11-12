
from datetime import date

from flask import Blueprint, request, jsonify, session

from server.extensions import db
from server.models import FoundItem, Category, Claim
from server.utils.decorators import login_required

found_items_bp = Blueprint("found_items", __name__)


def serialize_found_item(item):
    return {
        "id": item.id,
        "item_name": item.item_name,
        "description": item.description,
        "location": item.location,
        "date_found": item.date_found.isoformat(),
        "image_url": item.image_url,
        "status": item.status,
        "user_id": item.user_id,
        "category_id": item.category_id,
        "category": item.category.name
    }


@found_items_bp.route("/api/found-items", methods=["GET"])
def get_found_items():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid pagination values"}), 400

    query = FoundItem.query

    search = request.args.get("search", "").strip()

    if search:
        query = query.filter(FoundItem.item_name.ilike(f"%{search}%"))

    category_id = request.args.get("category_id", type=int)

    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(
        FoundItem.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [serialize_found_item(item) for item in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total
    }), 200


@found_items_bp.route("/api/found-items/<int:item_id>", methods=["GET"])
def get_found_item(item_id):
    item = db.session.get(FoundItem, item_id)

    if not item:
        return jsonify({"error": "Found item not found"}), 404

    return jsonify(serialize_found_item(item)), 200


@found_items_bp.route("/api/found-items", methods=["POST"])
@login_required
def create_found_item():
    data = request.get_json(silent=True) or {}

    required_fields = [
        "item_name", "description", "location",
        "date_found", "category_id"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    try:
        found_date = date.fromisoformat(data["date_found"])
        category_id = int(data["category_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date or category ID"}), 400

    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    item = FoundItem(
        item_name=data["item_name"].strip(),
        description=data["description"].strip(),
        location=data["location"].strip(),
        date_found=found_date,
        image_url=data.get("image_url"),
        user_id=session["user_id"],
        category_id=category_id
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Found item reported successfully",
        "item": serialize_found_item(item)
    }), 201


@found_items_bp.route("/api/found-items/<int:item_id>", methods=["PATCH"])
@login_required
def update_found_item(item_id):
    item = db.session.get(FoundItem, item_id)

    if not item:
        return jsonify({"error": "Found item not found"}), 404

    if item.user_id != session["user_id"]:
        return jsonify({"error": "You cannot edit this report"}), 403

    data = request.get_json(silent=True) or {}

    allowed_fields = ["item_name", "description", "location", "image_url"]

    for field in allowed_fields:
        if field in data:
            value = data[field]

            if field != "image_url" and (
                not isinstance(value, str) or not value.strip()
            ):
                return jsonify({"error": f"Invalid {field}"}), 400

            setattr(item, field, value.strip() if isinstance(value, str) else value)

    if "date_found" in data:
        try:
            item.date_found = date.fromisoformat(data["date_found"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid date_found"}), 400

    if "category_id" in data:
        try:
            category_id = int(data["category_id"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid category ID"}), 400

        if not db.session.get(Category, category_id):
            return jsonify({"error": "Category not found"}), 404

        item.category_id = category_id

    db.session.commit()

    return jsonify({
        "message": "Found item updated",
        "item": serialize_found_item(item)
    }), 200


@found_items_bp.route("/api/found-items/<int:item_id>", methods=["DELETE"])
@login_required
def delete_found_item(item_id):
    item = db.session.get(FoundItem, item_id)

    if not item:
        return jsonify({"error": "Found item not found"}), 404

    if item.user_id != session["user_id"]:
        return jsonify({"error": "You cannot delete this report"}), 403

    if item.claims:
        return jsonify({
            "error": "This item has claims. Resolve them before deleting it."
        }), 409

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Found item deleted"}), 200
