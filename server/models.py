
from datetime import datetime

from sqlalchemy import UniqueConstraint

from server.extensions import db, bcrypt


class University(db.Model):
    __tablename__ = "universities"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    code = db.Column(db.String(20), unique=True, nullable=False)

    users = db.relationship("User", back_populates="university")

    approved_credentials = db.relationship(
        "UniversityCredential",
        back_populates="university",
        cascade="all, delete-orphan",
    )


class UniversityCredential(db.Model):
    __tablename__ = "university_credentials"

    id = db.Column(db.Integer, primary_key=True)

    institutional_id = db.Column(db.String(50), nullable=False)
    institutional_email = db.Column(db.String(120), nullable=False)
    account_type = db.Column(db.String(20), nullable=False)
    is_registered = db.Column(db.Boolean, default=False, nullable=False)

    university_id = db.Column(
        db.Integer,
        db.ForeignKey("universities.id"),
        nullable=False,
    )

    university = db.relationship(
        "University",
        back_populates="approved_credentials",
    )

    __table_args__ = (
        UniqueConstraint(
            "university_id",
            "institutional_id",
            name="unique_university_institutional_id",
        ),
        UniqueConstraint(
            "university_id",
            "institutional_email",
            name="unique_university_institutional_email",
        ),
    )


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=True)

    # Approved institutional email
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Personal email for notifications and SendGrid
    contact_email = db.Column(
        db.String(120),
        unique=True,
        nullable=True,
    )

    institutional_id = db.Column(db.String(50), nullable=True)

    university_id = db.Column(
        db.Integer,
        db.ForeignKey("universities.id"),
        nullable=True,
    )

    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default="student", nullable=False)

    university = db.relationship("University", back_populates="users")

    lost_items = db.relationship("LostItem", back_populates="user")
    found_items = db.relationship("FoundItem", back_populates="user")
    claims = db.relationship("Claim", back_populates="user")
    notifications = db.relationship("Notification", back_populates="user")

    __table_args__ = (
        UniqueConstraint(
            "university_id",
            "institutional_id",
            name="unique_user_university_institutional_id",
        ),
    )

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.check_password_hash(
            self.password_hash, password
        )


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    lost_items = db.relationship("LostItem", back_populates="category")
    found_items = db.relationship("FoundItem", back_populates="category")


class LostItem(db.Model):
    __tablename__ = "lost_items"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_lost = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default="open", nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False,
    )

    user = db.relationship("User", back_populates="lost_items")
    category = db.relationship("Category", back_populates="lost_items")


class FoundItem(db.Model):
    __tablename__ = "found_items"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date_found = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(500))
    status = db.Column(db.String(20), default="available", nullable=False)
    handover_completed = db.Column(db.Boolean, default=False, nullable=False)
    handover_completed_at = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    category_id = db.Column(
        db.Integer,
        db.ForeignKey("categories.id"),
        nullable=False,
    )

    user = db.relationship("User", back_populates="found_items")

    category = db.relationship(
        "Category",
        back_populates="found_items",
    )

    claims = db.relationship("Claim", back_populates="found_item")


class Claim(db.Model):
    __tablename__ = "claims"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default="pending", nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    found_item_id = db.Column(
        db.Integer,
        db.ForeignKey("found_items.id"),
        nullable=False,
    )

    user = db.relationship("User", back_populates="claims")

    found_item = db.relationship(
        "FoundItem",
        back_populates="claims",
    )


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.Text, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False,
    )

    user = db.relationship("User", back_populates="notifications")
