
from functools import wraps
from flask import jsonify, session

from server.extensions import db
from server.models import User


def login_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Login required"}), 401

        user = db.session.get(User, user_id)

        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 401

        return route_function(*args, **kwargs)

    return wrapper


def admin_required(route_function):
    @wraps(route_function)
    def wrapper(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return jsonify({"error": "Login required"}), 401

        user = db.session.get(User, user_id)

        if not user:
            session.clear()
            return jsonify({"error": "User not found"}), 401

        if user.role != "admin":
            return jsonify({"error": "Administrator access required"}), 403

        return route_function(*args, **kwargs)

    return wrapper
