"""add domain and api auth fields to stores"""

from alembic import op
import sqlalchemy as sa

revision = '0006_store_api_credentials'
down_revision = '0005_admin_password_hash'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('stores', sa.Column('domain', sa.String(), nullable=True))
    op.add_column('stores', sa.Column('api_user', sa.String(), nullable=True))
    op.add_column('stores', sa.Column('api_password_hash', sa.String(), nullable=True))


def downgrade():
    op.drop_column('stores', 'api_password_hash')
    op.drop_column('stores', 'api_user')
    op.drop_column('stores', 'domain')
