
"""Add contact email to users

Revision ID: 7b5f6823f869
Revises: 4f790a1475e1
Create Date: 2026-11-25 11:24:05.018541

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7b5f6823f869'
down_revision = '4f790a1475e1'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'contact_email',
                sa.String(length=120),
                nullable=True
            )
        )

        batch_op.create_unique_constraint(
            'uq_users_contact_email',
            ['contact_email']
        )


def downgrade():
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_constraint(
            'uq_users_contact_email',
            type_='unique'
        )

        batch_op.drop_column('contact_email')
