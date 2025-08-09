"""add clients table and device-client relationship"""

from alembic import op
import sqlalchemy as sa

revision = "0003_clients"
down_revision = "0002_admin_table"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False, unique=True),
        sa.Column("permissions", sa.Text(), nullable=True),
    )
    op.add_column("devices", sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=True))

def downgrade():
    op.drop_column("devices", "client_id")
    op.drop_table("clients")
