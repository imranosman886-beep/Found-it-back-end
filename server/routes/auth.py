
from flask import Blueprint, request, jsonify, session
from server.extensions import db
from server.models import User

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Register a new user.
    ---
    tags:
      - Authentication
    summary: Create a new account
    description: Register a user with an email and password.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: student@example.com
            password:
              type: string
              example: password123
    responses:
      201:
        description: Account created successfully
      400:
        description: Missing email or password, or password too short
      409:
        description: Email already registered
    """
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered"}), 409

    user = User(email=email, role="student")
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Account created successfully",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in a user.
    ---
    tags:
      - Authentication
    summary: User login
    description: Authenticate a user and create a session.
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              example: student@example.com
            password:
              type: string
              example: password123
    responses:
      200:
        description: Login successful
      401:
        description: Invalid email or password
    """
    data = request.get_json(silent=True) or {}

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    user = User.query.filter_by(email=email).first()

    if not user or not isinstance(password, str) or not user.check_password(password):
        return jsonify({"error": "Invalid email or password"}), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.route("/check_session", methods=["GET"])
def check_session():
    """
    Check the current user's session.
    ---
    tags:
      - Authentication
    summary: Check session
    description: Check whether the current user is logged in.
    responses:
      200:
        description: Session status returned successfully
    """
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"logged_in": False}), 200

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({"logged_in": False}), 200

    return jsonify({
        "logged_in": True,
        "user": {
            "id": user.id,
            "email": user.email,
            "role": user.role
        }
    }), 200


@auth_bp.route("/logout", methods=["DELETE"])
def logout():
    """
    Log out the current user.
    ---
    tags:
      - Authentication
    summary: User logout
    description: Clear the current user's session.
    responses:
      200:
        description: Logged out successfully
    """
    session.clear()

    return jsonify({"message": "Logged out successfully"}), 200
