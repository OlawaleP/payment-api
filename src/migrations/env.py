from alembic import context
from sqlalchemy import engine_from_config, pool
from logging.config import fileConfig
import os
from src.core.models import Base

config = context.config
config.set_main_option('sqlalchemy.url', 'postgresql://fintech_user:secure_password@localhost:5432/fintech')
fileConfig(config.config_file_name)
connectable = engine_from_config(config.get_section(config.config_ini_section), prefix='sqlalchemy.', poolclass=pool.NullPool)
with connectable.connect() as connection:
    context.configure(
        connection=connection,
        target_metadata=Base.metadata
    )
    with context.begin_transaction():
        context.run_migrations()