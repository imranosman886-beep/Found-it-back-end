
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

        demo_credentials = [
            {
                "institutional_id": "MOR-STU-001",
                "institutional_email": "student001@moringaschool.com",
                "account_type": "student",
            },
            {
                "institutional_id": "MOR-STU-002",
                "institutional_email": "student002@moringaschool.com",
                "account_type": "student",
            },
            {
                "institutional_id": "MOR-STF-001",
                "institutional_email": "staff001@moringaschool.com",
                "account_type": "staff",
            },
        ]

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


if __name__ == "__main__":
    seed_university()
