import cloudinary.uploader
from flask import Blueprint, request, jsonify
from server.utils.decorators import login_required
from server.utils.cloudinary_config import configure_cloudinary

uploads_bp = Blueprint("uploads", __name__)


@uploads_bp.route("/api/upload-image", methods=["POST"])
@login_required
def upload_image():
    if "image" not in request.files:
        return jsonify({"error": "Image file is required"}), 400

    image = request.files["image"]

    if not image.filename:
        return jsonify({"error": "No image selected"}), 400

    allowed_extensions = {"png", "jpg", "jpeg", "webp"}

    extension = image.filename.rsplit(".", 1)[-1].lower()

    if "." not in image.filename or extension not in allowed_extensions:
        return jsonify({"error": "Unsupported image format"}), 400

    configure_cloudinary()

    result = cloudinary.uploader.upload(
        image,
        folder="foundit/items",
        resource_type="image"
    )

    return jsonify({
        "message": "Image uploaded successfully",
        "image_url": result["secure_url"]
    }), 201
