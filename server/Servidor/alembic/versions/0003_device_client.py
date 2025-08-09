from alembic import op
import sqlalchemy as sa

revision = '0003_device_client'
down_revision = '0002_admin_table'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('devices', sa.Column('client_id', sa.String(), nullable=True))


def downgrade():
    op.drop_column('devices', 'client_id')
