from alembic import op
import sqlalchemy as sa

revision = '0001_create_admin'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'admins',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user', sa.String(255)),
        sa.Column('action', sa.String(255)),
        sa.Column('target', sa.String(255)),
        sa.Column('ip', sa.String(45)),
        sa.Column('ua', sa.String(255)),
        sa.Column('timestamp', sa.DateTime, nullable=False, server_default=sa.func.now()),
        sa.Column('result', sa.String(50)),
    )

def downgrade():
    op.drop_table('audit_logs')
    op.drop_table('admins')
