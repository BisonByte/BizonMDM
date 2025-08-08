from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys

# Add app path
target_metadata = None

config = context.config

fileConfig(config.config_file_name)

# Interpret DB URL from config.ini
section = config.get_section(config.config_ini_section)

if os.getenv('DATABASE_URL'):
    section['sqlalchemy.url'] = os.getenv('DATABASE_URL')

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from models import Base  # noqa

target_metadata = Base.metadata

def run_migrations_offline():
    context.configure(url=section['sqlalchemy.url'], target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    engine = engine_from_config(section, prefix='', poolclass=pool.NullPool)
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
