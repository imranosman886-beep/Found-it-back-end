
import pytest
from datetime import date

from server import create_app
from server.extensions import db
from server.models import (
    User,
    Category,
    LostItem,
    FoundItem,
)


@pytest.fixture
def app():
    test_app = create_app({
        "TESTING": True,
        "SECRET_KEY": "test-secret-key",
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    })

    with test_app.app_context():
        db.create_all()

        yield test_app

        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def student(app):
    with app.app_context():
        user = User(
            email="student@test.com",
            role="student",
        )
        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        return user.id


@pytest.fixture
def another_student(app):
    with app.app_context():
        user = User(
            email="another@test.com",
            role="student",
        )
        user.set_password("password123")

        db.session.add(user)
        db.session.commit()

        return user.id


@pytest.fixture
def admin(app):
    with app.app_context():
        user = User(
            email="admin@test.com",
            role="admin",
        )
        user.set_password("adminpass123")

        db.session.add(user)
        db.session.commit()

        return user.id


@pytest.fixture
def category(app):
    with app.app_context():
        new_category = Category(name="Electronics")

        db.session.add(new_category)
        db.session.commit()

        return new_category.id


@pytest.fixture
def lost_item(app, student, category):
    with app.app_context():
        item = LostItem(
            item_name="Blue Backpack",
            description="A blue backpack with books inside",
            location="Library",
            date_lost=date(2026, 11, 1),
            status="open",
            user_id=student,
            category_id=category,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


@pytest.fixture
def found_item(app, student, category):
    with app.app_context():
        item = FoundItem(
            item_name="Black Phone",
            description="A black smartphone",
            location="Cafeteria",
            date_found=date(2026, 11, 2),
            status="available",
            user_id=student,
            category_id=category,
        )

        db.session.add(item)
        db.session.commit()

        return item.id


@pytest.fixture
def login_student(client):
    response = client.post(
        "/login",
        json={
            "email": "student@test.com",
            "password": "password123",
        },
    )
    return response


@pytest.fixture
def login_admin(client):
    response = client.post(
        "/login",
        json={
            "email": "admin@test.com",
            "password": "adminpass123",
        },
    )
    return response
