
from server import create_app
from server.extensions import db
from server.models import University, UniversityCredential


app = create_app()


def seed_university():
    with app.app_context():

        university = University.query.filter_by(
            code="MOR"
        ).first()

        if not university:
            university = University(
                name="Moringa School",
                code="MOR",
            )

            db.session.add(university)
            db.session.commit()

        demo_credentials = []

        # Create 15 student credentials.
        for number in range(1, 16):
            demo_credentials.append({
                "institutional_id": f"MOR-STU-{number:03d}",
                "institutional_email": (
                    f"student{number:03d}@moringaschool.com"
                ),
                "account_type": "student",
            })

        # Create 15 staff credentials.
        for number in range(1, 16):
            demo_credentials.append({
                "institutional_id": f"MOR-STF-{number:03d}",
                "institutional_email": (
                    f"staff{number:03d}@moringaschool.com"
                ),
                "account_type": "staff",
            })

        # Save credentials without creating duplicates.
        for credential in demo_credentials:
            existing = UniversityCredential.query.filter_by(
                university_id=university.id,
                institutional_id=credential["institutional_id"],
            ).first()

            if not existing:
                new_credential = UniversityCredential(
                    university_id=university.id,
                    institutional_id=credential["institutional_id"],
                    institutional_email=credential["institutional_email"],
                    account_type=credential["account_type"],
                )

                db.session.add(new_credential)

        db.session.commit()

        print("Demo university records created successfully.")
        print("15 student credentials and 15 staff credentials checked.")


if __name__ == "__main__":
    seed_university()
