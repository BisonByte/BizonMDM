"""add user and client tables"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0003_user_client_tables"
down_revision = "0002_admin_table"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
    )
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
    )
    op.create_table(
        "client_devices",
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), primary_key=True),
        sa.Column("device_id", sa.Integer(), sa.ForeignKey("devices.id"), primary_key=True),
    )


def downgrade():
    op.drop_table("client_devices")
    op.drop_table("clients")
    op.drop_table("users")
