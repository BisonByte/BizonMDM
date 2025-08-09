"""rename password column to password_hash and hash existing passwords"""

from alembic import op
import sqlalchemy as sa
import bcrypt

# revision identifiers, used by Alembic.
revision = '0005_admin_password_hash'
down_revision = '0004_client_permissions'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('admins', sa.Column('password_hash', sa.String(), nullable=True))
    conn = op.get_bind()
    admins = conn.execute(sa.text('SELECT id, password FROM admins')).fetchall()
    for admin in admins:
        hashed = bcrypt.hashpw(admin.password.encode(), bcrypt.gensalt()).decode()
        conn.execute(sa.text('UPDATE admins SET password_hash=:hash WHERE id=:id'), {'hash': hashed, 'id': admin.id})
    op.drop_column('admins', 'password')
    op.alter_column('admins', 'password_hash', nullable=False)


def downgrade():
    op.add_column('admins', sa.Column('password', sa.String(), nullable=True))
    conn = op.get_bind()
    admins = conn.execute(sa.text('SELECT id, password_hash FROM admins')).fetchall()
    for admin in admins:
        conn.execute(sa.text('UPDATE admins SET password=:hash WHERE id=:id'), {'hash': admin.password_hash, 'id': admin.id})
    op.drop_column('admins', 'password_hash')
    op.alter_column('admins', 'password', nullable=False)
