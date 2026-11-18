
"""Add handover tracking columns to found items

Revision ID: 242b75df6ed2
Revises: 24197f28177f
Create Date: 2026-11-18 10:27:31.213414

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '242b75df6ed2'
down_revision = '24197f28177f'
branch_labels = None
depends_on = None


def upgrade():
    # Add handover tracking columns.
    # Existing records will receive False as their default value.
    with op.batch_alter_table('found_items', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                'handover_completed',
                sa.Boolean(),
                nullable=False,
                server_default=sa.false()
            )
        )

        batch_op.add_column(
            sa.Column(
                'handover_completed_at',
                sa.DateTime(),
                nullable=True
            )
        )

    # Remove the database default after existing records are updated.
    with op.batch_alter_table('found_items', schema=None) as batch_op:
        batch_op.alter_column(
            'handover_completed',
            server_default=None
        )


def downgrade():
    # Remove the handover tracking columns if this migration is rolled back.
    with op.batch_alter_table('found_items', schema=None) as batch_op:
        batch_op.drop_column('handover_completed_at')
        batch_op.drop_column('handover_completed')
