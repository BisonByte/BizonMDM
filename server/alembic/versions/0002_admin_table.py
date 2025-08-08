"""create admins table"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0002_admin_table"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "admins",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(), nullable=False, unique=True),
        sa.Column("password", sa.String(), nullable=False),
        sa.Column("created", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("admins")
