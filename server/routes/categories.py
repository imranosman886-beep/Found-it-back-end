
from flask import Blueprint, request, jsonify

from server.extensions import db
from server.models import Category
from server.utils.decorators import admin_required

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/api/categories", methods=["GET"])
def get_categories():
    """
    Get all categories.
    ---
    tags:
      - Categories
    responses:
      200:
        description: List of categories
    """
    categories = Category.query.order_by(Category.name).all()

    return jsonify([
        {"id": category.id, "name": category.name}
        for category in categories
    ]), 200


@categories_bp.route("/api/categories", methods=["POST"])
@admin_required
def create_category():
    """
    Create a category.
    ---
    tags:
      - Categories
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
          properties:
            name:
              type: string
              example: Electronics
    responses:
      201:
        description: Category created
      400:
        description: Category name is required
      409:
        description: Category already exists
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category already exists"}), 409

    category = Category(name=name)

    db.session.add(category)
    db.session.commit()

    return jsonify({
        "message": "Category created",
        "category": {"id": category.id, "name": category.name}
    }), 201


@categories_bp.route("/api/categories/<int:category_id>", methods=["DELETE"])
@admin_required
def delete_category(category_id):
    """
    Delete a category.
    ---
    tags:
      - Categories
    parameters:
      - name: category_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Category deleted
      404:
        description: Category not found
      409:
        description: Category is currently being used
    """
    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({"error": "Category not found"}), 404

    if category.lost_items or category.found_items:
        return jsonify({
            "error": "Cannot delete a category that is being used"
        }), 409

    db.session.delete(category)
    db.session.commit()

    return jsonify({"message": "Category deleted"}), 200
