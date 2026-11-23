
from datetime import date

from flask import Blueprint, request, jsonify, session

from server.extensions import db
from server.models import LostItem, Category
from server.utils.decorators import login_required

lost_items_bp = Blueprint("lost_items", __name__)


def serialize_lost_item(item):
    return {
        "id": item.id,
        "item_name": item.item_name,
        "description": item.description,
        "location": item.location,
        "date_lost": item.date_lost.isoformat(),
        "image_url": item.image_url,
        "status": item.status,
        "user_id": item.user_id,
        "category_id": item.category_id,
        "category": item.category.name
    }


@lost_items_bp.route("/api/lost-items", methods=["GET"])
def get_lost_items():
    """
    Get all lost items.
    ---
    tags:
      - Lost Items
    parameters:
      - name: page
        in: query
        type: integer
        default: 1
      - name: per_page
        in: query
        type: integer
        default: 10
      - name: search
        in: query
        type: string
      - name: category_id
        in: query
        type: integer
    responses:
      200:
        description: Paginated lost items
      400:
        description: Invalid pagination values
    """
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    if page < 1 or per_page < 1 or per_page > 100:
        return jsonify({"error": "Invalid pagination values"}), 400

    query = LostItem.query
    search = request.args.get("search", "").strip()

    if search:
        query = query.filter(LostItem.item_name.ilike(f"%{search}%"))

    category_id = request.args.get("category_id", type=int)

    if category_id:
        query = query.filter_by(category_id=category_id)

    pagination = query.order_by(
        LostItem.id.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "items": [serialize_lost_item(item) for item in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "total": pagination.total
    }), 200


@lost_items_bp.route("/api/lost-items/<int:item_id>", methods=["GET"])
def get_lost_item(item_id):
    """
    Get one lost item.
    ---
    tags:
      - Lost Items
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lost item details
      404:
        description: Lost item not found
    """
    item = db.session.get(LostItem, item_id)

    if not item:
        return jsonify({"error": "Lost item not found"}), 404

    return jsonify(serialize_lost_item(item)), 200


@lost_items_bp.route("/api/lost-items", methods=["POST"])
@login_required
def create_lost_item():
    """
    Report a lost item.
    ---
    tags:
      - Lost Items
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - item_name
            - description
            - location
            - date_lost
            - category_id
          properties:
            item_name:
              type: string
              example: Black backpack
            description:
              type: string
              example: Black backpack with a laptop inside
            location:
              type: string
              example: Main library
            date_lost:
              type: string
              format: date
              example: "2026-11-15"
            category_id:
              type: integer
              example: 1
            image_url:
              type: string
              example: https://example.com/image.jpg
    responses:
      201:
        description: Lost item reported
      400:
        description: Missing or invalid information
      404:
        description: Category not found
    """
    data = request.get_json(silent=True) or {}

    required_fields = [
        "item_name", "description", "location",
        "date_lost", "category_id"
    ]

    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    try:
        lost_date = date.fromisoformat(data["date_lost"])
        category_id = int(data["category_id"])
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date or category ID"}), 400

    if lost_date > date.today():
        return jsonify({"error": "Lost date cannot be in the future"}), 400

    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    item = LostItem(
        item_name=data["item_name"].strip(),
        description=data["description"].strip(),
        location=data["location"].strip(),
        date_lost=lost_date,
        image_url=data.get("image_url"),
        user_id=session["user_id"],
        category_id=category_id
    )

    db.session.add(item)
    db.session.commit()

    return jsonify({
        "message": "Lost item reported successfully",
        "item": serialize_lost_item(item)
    }), 201


@lost_items_bp.route("/api/lost-items/<int:item_id>", methods=["PATCH"])
@login_required
def update_lost_item(item_id):
    """
    Update your lost item report.
    ---
    tags:
      - Lost Items
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
          properties:
            item_name:
              type: string
            description:
              type: string
            location:
              type: string
            image_url:
              type: string
            date_lost:
              type: string
              format: date
            category_id:
              type: integer
    responses:
      200:
        description: Lost item updated
      400:
        description: Invalid information
      403:
        description: You cannot edit this report
      404:
        description: Lost item or category not found
    """
    item = db.session.get(LostItem, item_id)

    if not item:
        return jsonify({"error": "Lost item not found"}), 404

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

    if "date_lost" in data:
        try:
            lost_date = date.fromisoformat(data["date_lost"])
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid date_lost"}), 400

        if lost_date > date.today():
            return jsonify({"error": "Lost date cannot be in the future"}), 400

        item.date_lost = lost_date

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
        "message": "Lost item updated",
        "item": serialize_lost_item(item)
    }), 200


@lost_items_bp.route("/api/lost-items/<int:item_id>", methods=["DELETE"])
@login_required
def delete_lost_item(item_id):
    """
    Delete your lost item report.
    ---
    tags:
      - Lost Items
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Lost item deleted
      403:
        description: You cannot delete this report
      404:
        description: Lost item not found
    """
    item = db.session.get(LostItem, item_id)

    if not item:
        return jsonify({"error": "Lost item not found"}), 404

    if item.user_id != session["user_id"]:
        return jsonify({"error": "You cannot delete this report"}), 403

    db.session.delete(item)
    db.session.commit()

    return jsonify({"message": "Lost item deleted"}), 200
