
from flask import Blueprint, request, jsonify

from server.extensions import db
from server.models import Category
from server.utils.decorators import admin_required

categories_bp = Blueprint("categories", __name__)


@categories_bp.route("/api/categories", methods=["GET"])
def get_categories():
    categories = Category.query.order_by(Category.name).all()

    return jsonify([
        {"id": category.id, "name": category.name}
        for category in categories
    ]), 200


@categories_bp.route("/api/categories", methods=["POST"])
@admin_required
def create_category():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()

    if not name:
        return jsonify({"error": "Category name is required"}), 400

    if Category.query.filter_by(name=name).first():
        return jsonify({"error": "Category is already existing"}), 409

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
