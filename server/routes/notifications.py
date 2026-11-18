
from flask import Blueprint, jsonify, session

from server.extensions import db
from server.models import Notification
from server.utils.decorators import login_required

notifications_bp = Blueprint("notifications", __name__)


def serialize_notification(notification):
    return {
        "id": notification.id,
        "message": notification.message,
        "is_read": notification.is_read,
        "user_id": notification.user_id
    }


@notifications_bp.route("/api/notifications", methods=["GET"])
@login_required
def get_notifications():
    """
    Get your notifications.
    ---
    tags:
      - Notifications
    responses:
      200:
        description: List of your notifications
    """
    notifications = Notification.query.filter_by(
        user_id=session["user_id"]
    ).order_by(Notification.id.desc()).all()

    return jsonify([
        serialize_notification(notification)
        for notification in notifications
    ]), 200


@notifications_bp.route(
    "/api/notifications/<int:notification_id>/read",
    methods=["PATCH"]
)
@login_required
def mark_notification_read(notification_id):
    """
    Mark a notification as read.
    ---
    tags:
      - Notifications
    parameters:
      - name: notification_id
        in: path
        type: integer
        required: true
    responses:
      200:
        description: Notification marked as read
      403:
        description: You cannot access this notification
      404:
        description: Notification not found
    """
    notification = db.session.get(Notification, notification_id)

    if not notification:
        return jsonify({"error": "Notification not found"}), 404

    if notification.user_id != session["user_id"]:
        return jsonify({"error": "You cannot access this notification"}), 403

    notification.is_read = True
    db.session.commit()

    return jsonify({
        "message": "Notification marked as read",
        "notification": serialize_notification(notification)
    }), 200
