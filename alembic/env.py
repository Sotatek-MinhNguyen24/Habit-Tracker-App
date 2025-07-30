from logging.config import fileConfig
import os
# Import create_engine (phiên bản đồng bộ)
from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# Import các models của bạn để Alembic có thể phát hiện các bảng
# Đảm bảo rằng tất cả các module chứa model đều được import ở đây
from app.features.habits import models as habits_models
from app.features.users import models as users_models

# Import Base từ file database.py của bạn
from app.core.database import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Lấy URL kết nối từ alembic.ini
    # Dòng này sẽ lấy URL đã được bạn cấu hình là URL đồng bộ trong alembic.ini
    db_url = os.getenv("ALEMBIC_DATABASE_URL", config.get_main_option("sqlalchemy.url"))
    if not db_url:
        raise Exception("Database URL for Alembic is not set. Please set ALEMBIC_DATABASE_URL or sqlalchemy.url in alembic.ini")
    # Tạo một SQLAlchemy Engine ĐỒNG BỘ
    # Đảm bảo rằng URL trong alembic.ini không phải là dạng 'postgresql+asyncpg'
    connectable = create_engine(
        db_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()