"""Add logical_id to templates and update versions

Revision ID: 002
Revises: 001
Create Date: 2025-11-12 14:31:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add logical_id column to templates
    op.add_column('templates', sa.Column('logical_id', sa.String(), nullable=False, default=''))

    # Update versions table to use logical_id
    op.add_column('versions', sa.Column('template_logical_id', sa.String(), nullable=True))
    op.drop_constraint('versions_template_id_fkey', 'versions', type_='foreignkey')

    # Migrate data: set logical_id to id for existing templates
    op.execute("UPDATE templates SET logical_id = id WHERE logical_id = ''")

    # Migrate version data
    op.execute("UPDATE versions SET template_logical_id = (SELECT logical_id FROM templates WHERE templates.id = versions.template_id)")

    # Make template_logical_id not nullable and drop old column
    op.alter_column('versions', 'template_logical_id', nullable=False)
    op.drop_column('versions', 'template_id')


def downgrade() -> None:
    # Revert versions table changes
    op.add_column('versions', sa.Column('template_id', sa.String(), nullable=True))
    op.execute("UPDATE versions SET template_id = (SELECT id FROM templates WHERE templates.logical_id = versions.template_logical_id)")
    op.alter_column('versions', 'template_id', nullable=False)
    op.create_foreign_key('versions_template_id_fkey', 'versions', 'templates', ['template_id'], ['id'])
    op.drop_column('versions', 'template_logical_id')

    # Drop logical_id column
    op.drop_column('templates', 'logical_id')
