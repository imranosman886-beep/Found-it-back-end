
"""add university verification

Revision ID: 4f790a1475e1
Revises: 242b75df6ed2
Create Date: 2026-11-23 11:24:14.764180

"""

from alembic import op
import sqlalchemy as sa


# Revision identifiers
revision = "4f790a1475e1"
down_revision = "242b75df6ed2"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "universities",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "university_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("institutional_id", sa.String(length=50), nullable=False),
        sa.Column("institutional_email", sa.String(length=120), nullable=False),
        sa.Column("account_type", sa.String(length=20), nullable=False),
        sa.Column(
            "is_registered",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.Column("university_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["university_id"],
            ["universities.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "university_id",
            "institutional_email",
            name="unique_university_institutional_email",
        ),
        sa.UniqueConstraint(
            "university_id",
            "institutional_id",
            name="unique_university_institutional_id",
        ),
    )

    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("full_name", sa.String(length=120), nullable=True)
        )
        batch_op.add_column(
            sa.Column("institutional_id", sa.String(length=50), nullable=True)
        )
        batch_op.add_column(
            sa.Column("university_id", sa.Integer(), nullable=True)
        )
        batch_op.create_unique_constraint(
            "unique_user_university_institutional_id",
            ["university_id", "institutional_id"],
        )
        batch_op.create_foreign_key(
            "fk_users_university_id_universities",
            "universities",
            ["university_id"],
            ["id"],
        )


def downgrade():
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_constraint(
            "fk_users_university_id_universities",
            type_="foreignkey",
        )
        batch_op.drop_constraint(
            "unique_user_university_institutional_id",
            type_="unique",
        )
        batch_op.drop_column("university_id")
        batch_op.drop_column("institutional_id")
        batch_op.drop_column("full_name")

    op.drop_table("university_credentials")
    op.drop_table("universities")
