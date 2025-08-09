"""add permissions field to clients"""

from alembic import op
import sqlalchemy as sa

revision = '0004_client_permissions'
down_revision = '0003_user_client_tables'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('clients', sa.Column('permissions', sa.Text(), nullable=False, server_default='[]'))


def downgrade():
    op.drop_column('clients', 'permissions')
