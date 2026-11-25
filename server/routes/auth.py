
from flask import Blueprint, request, jsonify, session
from sqlalchemy.exc import IntegrityError

from server.extensions import db
from server.models import User, University, UniversityCredential
from server.services.email_service import send_email


auth_bp = Blueprint("auth", __name__)


def get_json_data():
    """Return the request JSON if it is a valid object."""

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return None, (
            jsonify({"error": "Request body must be a JSON object"}),
            400,
        )

    return data, None


def validate_password(password):
    """Validate password strength."""

    if not isinstance(password, str):
        return jsonify({
            "error": "Password must be a string"
        }), 400

    if len(password) < 8:
        return jsonify({
            "error": "Password must be at least 8 characters"
        }), 400

    if len(password.encode("utf-8")) > 72:
        return jsonify({
            "error": "Password must not exceed 72 bytes"
        }), 400

    if not any(char.isupper() for char in password):
        return jsonify({
            "error": "Password must contain at least one uppercase letter"
        }), 400

    if not any(char.islower() for char in password):
        return jsonify({
            "error": "Password must contain at least one lowercase letter"
        }), 400

    if not any(char.isdigit() for char in password):
        return jsonify({
            "error": "Password must contain at least one number"
        }), 400

    return None


def validate_email(email):
    """Perform basic email address validation."""

    if not isinstance(email, str):
        return False

    email = email.strip()

    if len(email) > 120:
        return False

    if "@" not in email:
        return False

    local_part, separator, domain = email.partition("@")

    return bool(
        separator
        and local_part
        and domain
        and "." in domain
        and not domain.startswith(".")
        and not domain.endswith(".")
    )


@auth_bp.route("/signup", methods=["POST"])
def signup():
    """
    Register a student or staff member,
    send a welcome email, and automatically log them in.
    """

    data, error = get_json_data()

    if error:
        return error

    full_name = data.get("full_name")
    email = data.get("email")
    contact_email = data.get("contact_email")
    institutional_id = data.get("institutional_id")
    university_code = data.get("university_code")
    account_type = data.get("account_type")
    password = data.get("password")

    if not all([
        full_name,
        email,
        contact_email,
        institutional_id,
        university_code,
        account_type,
        password,
    ]):
        return jsonify({
            "error": "All registration fields are required"
        }), 400

    if not all(isinstance(value, str) for value in [
        full_name,
        email,
        contact_email,
        institutional_id,
        university_code,
        account_type,
        password,
    ]):
        return jsonify({
            "error": "All registration fields must be strings"
        }), 400

    full_name = full_name.strip()
    email = email.strip().lower()
    contact_email = contact_email.strip().lower()
    institutional_id = institutional_id.strip().upper()
    university_code = university_code.strip().upper()
    account_type = account_type.strip().lower()

    if not full_name:
        return jsonify({
            "error": "Full name is required"
        }), 400

    if not validate_email(email):
        return jsonify({
            "error": "Please provide a valid institutional email address"
        }), 400

    if not validate_email(contact_email):
        return jsonify({
            "error": "Please provide a valid personal contact email address"
        }), 400

    if email == contact_email:
        return jsonify({
            "error": "Personal email must be different from institutional email"
        }), 400

    if account_type not in ["student", "staff"]:
        return jsonify({
            "error": "Account type must be student or staff"
        }), 400

    password_error = validate_password(password)

    if password_error:
        return password_error

    university = University.query.filter_by(
        code=university_code
    ).first()

    if not university:
        return jsonify({
            "error": "University not found"
        }), 404

    credential = UniversityCredential.query.filter_by(
        university_id=university.id,
        institutional_id=institutional_id,
    ).first()

    if not credential:
        return jsonify({
            "error": "Institutional ID is not approved"
        }), 403

    if credential.institutional_email.lower() != email:
        return jsonify({
            "error": "Email does not match the approved institutional record"
        }), 403

    if credential.account_type != account_type:
        return jsonify({
            "error": "Account type does not match the approved record"
        }), 403

    if credential.is_registered:
        return jsonify({
            "error": "This institutional ID has already been registered"
        }), 409

    if User.query.filter_by(email=email).first():
        return jsonify({
            "error": "Institutional email already registered"
        }), 409

    if User.query.filter_by(contact_email=contact_email).first():
        return jsonify({
            "error": "Personal contact email already registered"
        }), 409

    user = User(
        full_name=full_name,
        email=email,
        contact_email=contact_email,
        institutional_id=institutional_id,
        university_id=university.id,
        role=account_type,
    )

    user.set_password(password)

    try:
        db.session.add(user)
        credential.is_registered = True
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            "error": "This account information is already registered"
        }), 409

    # Automatically create a session after successful signup.
    session.clear()
    session["user_id"] = user.id

    # Send the welcome email to the user's personal email.
    email_sent = False

    try:
        email_sent = send_email(
            to_email=user.contact_email,
            subject="Welcome to FoundIt!",
            content=(
                f"Hello {user.full_name},\n\n"
                "Welcome to FoundIt!\n\n"
                "Your account has been created successfully. "
                "You can now use FoundIt to report lost items, "
                "report found items, and help reunite people "
                "with their belongings.\n\n"
                "Thank you for joining our community!\n\n"
                "The FoundIt Team"
            ),
        )

        print("WELCOME EMAIL RESULT:", email_sent)

    except Exception as error:
        print("WELCOME EMAIL ERROR:", str(error))
        email_sent = False

    return jsonify({
        "message": "Account created successfully",
        "welcome_email_sent": email_sent,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "contact_email": user.contact_email,
            "institutional_id": user.institutional_id,
            "university": university.name,
            "role": user.role,
        },
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Log in a user using their institutional ID and password.
    Existing legacy accounts can still use email login.
    """

    data, error = get_json_data()

    if error:
        return error

    password = data.get("password")
    institutional_id = data.get("institutional_id")
    email = data.get("email")

    if not isinstance(password, str):
        return jsonify({
            "error": "Password must be a string"
        }), 400

    if not password:
        return jsonify({
            "error": "Password is required"
        }), 400

    if institutional_id is not None:
        if not isinstance(institutional_id, str):
            return jsonify({
                "error": "Institutional ID must be a string"
            }), 400

        institutional_id = institutional_id.strip().upper()

        if not institutional_id:
            return jsonify({
                "error": "Institutional ID is required"
            }), 400

        user = User.query.filter_by(
            institutional_id=institutional_id
        ).first()

    elif email is not None:
        if not isinstance(email, str):
            return jsonify({
                "error": "Email must be a string"
            }), 400

        email = email.strip().lower()

        if not email:
            return jsonify({
                "error": "Email is required"
            }), 400

        user = User.query.filter_by(email=email).first()

        if user and user.institutional_id:
            user = None

    else:
        return jsonify({
            "error": "Institutional ID and password are required"
        }), 400

    if not user or not user.check_password(password):
        return jsonify({
            "error": "Invalid institutional ID or password"
        }), 401

    session.clear()
    session["user_id"] = user.id

    return jsonify({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "contact_email": user.contact_email,
            "institutional_id": user.institutional_id,
            "role": user.role,
        },
    }), 200


@auth_bp.route("/check_session", methods=["GET"])
def check_session():
    """Check the current user's session."""

    user_id = session.get("user_id")

    if not user_id:
        return jsonify({
            "logged_in": False
        }), 200

    user = db.session.get(User, user_id)

    if not user:
        session.clear()
        return jsonify({
            "logged_in": False
        }), 200

    return jsonify({
        "logged_in": True,
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "email": user.email,
            "contact_email": user.contact_email,
            "institutional_id": user.institutional_id,
            "role": user.role,
        },
    }), 200


@auth_bp.route("/logout", methods=["DELETE"])
def logout():
    """Log out the current user."""

    session.clear()

    return jsonify({
        "message": "Logged out successfully"
    }), 200
