
import os
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_email(to_email, subject, content):
    """
    Send an email using SendGrid.

    Args:
        to_email: Recipient's email address.
        subject: Email subject.
        content: Plain-text email content.

    Returns:
        True if the email was accepted by SendGrid.
        False if sending failed.
    """
    api_key = current_app.config.get("SENDGRID_API_KEY")

    if not api_key:
        current_app.logger.error("SendGrid API key is missing.")
        return False

    sender_email = os.getenv("SENDGRID_FROM_EMAIL")

    if not sender_email:
        current_app.logger.error("SendGrid sender email is missing.")
        return False

    message = Mail(
        from_email=sender_email,
        to_emails=to_email,
        subject=subject,
        plain_text_content=content
    )

    try:
        sendgrid_client = SendGridAPIClient(api_key)
        response = sendgrid_client.send(message)

        if response.status_code in (200, 201, 202):
            current_app.logger.info("Email accepted by SendGrid.")
            return True

        current_app.logger.error(
            "SendGrid returned status %s", response.status_code
        )
        return False

    except Exception:
        current_app.logger.exception("Failed to send email.")
        return False
