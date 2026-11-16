
from app import app
from server.services.email_service import send_email

with app.app_context():
    success = send_email(
        to_email="YOUR_EMAIL@example.com",
        subject="FoundIt - SendGrid Test",
        content="Congratulations! Your FoundIt backend can now send emails using SendGrid."
    )

    if success:
        print("SUCCESS: SendGrid accepted the email!")
    else:
        print("FAILED: Check your SendGrid configuration.")
