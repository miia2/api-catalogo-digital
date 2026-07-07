import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 1. Ajuste de caminhos no topo (Garante que tudo abaixo funcione)
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 2. Centralizando TODOS os imports do seu app aqui em cima
from app.core.config import settings
from app.models import Base 
from app.core.database import SQLALCHEMY_DATABASE_URL # Mapeado aqui no topo!

# Objeto de configuração do Alembic
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

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
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    
    configuration = config.get_section(config.config_ini_section) or {}
    # Forçamos o Alembic a usar a URL correta (Seja SQLite local ou Postgres do Supabase)
    configuration["sqlalchemy.url"] = SQLALCHEMY_DATABASE_URL
    # --------------------------------------

    connect_into = context.config.attributes.get("connection", None)
    
    if connect_into is None:
        # Passamos a nossa configuração atualizada para o motor do Alembic
        connect_into = engine_from_config(
            configuration,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )

    with connect_into.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
