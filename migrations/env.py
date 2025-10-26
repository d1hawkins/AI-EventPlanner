import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from sqlalchemy.engine.url import make_url

from alembic import context

from app.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Override the sqlalchemy.url with the DATABASE_URL from environment
database_url = os.environ.get("DATABASE_URL")
if database_url:
    # Convert postgres:// to postgresql:// for SQLAlchemy 2.0 compatibility
    # SQLAlchemy 2.0+ requires 'postgresql://' as the dialect name
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
        print("INFO: Converted postgres:// URL to postgresql:// for SQLAlchemy 2.0 compatibility")

    # URL-encode username and password for Azure PostgreSQL compatibility
    # Azure usernames contain @ which must be encoded for SQLAlchemy
    try:
        from urllib.parse import urlparse, quote, urlunparse
        parsed = urlparse(database_url)

        if parsed.username and parsed.password:
            # Check if username contains @ (Azure PostgreSQL format: user@server)
            if '@' in parsed.username:
                # URL-encode the username and password
                encoded_username = quote(parsed.username, safe='')
                encoded_password = quote(parsed.password, safe='')

                # Reconstruct the netloc with encoded credentials
                netloc = f"{encoded_username}:{encoded_password}@{parsed.hostname}"
                if parsed.port:
                    netloc += f":{parsed.port}"

                # Reconstruct the full URL
                database_url = urlunparse((
                    parsed.scheme,
                    netloc,
                    parsed.path,
                    parsed.params,
                    parsed.query,
                    parsed.fragment
                ))

                print("INFO: URL-encoded credentials for Azure PostgreSQL compatibility")
    except Exception as e:
        print(f"WARNING: Could not URL-encode credentials: {e}")
        # Continue with the original URL

    config.set_main_option("sqlalchemy.url", database_url)
    # Mask the password in the URL for logging
    masked_url = database_url
    if '@' in database_url:
        parts = database_url.split('@')
        if len(parts) > 1:
            credentials = parts[0].split(':')
            if len(credentials) > 2:
                masked_url = f"{credentials[0]}:{credentials[1]}:****@{parts[1]}"
            elif len(credentials) > 1:
                masked_url = f"{credentials[0]}:****@{parts[1]}"
    print(f"Using database URL: {masked_url}")
else:
    # Fallback to the one in config file
    print("WARNING: DATABASE_URL environment variable not set, using default from alembic.ini")


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    
    # Determine the dialect based on the URL
    dialect = make_url(url).get_dialect().name
    print(f"Using dialect: {dialect}")
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        dialect_name="postgresql"
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Get the configuration section
    cfg = config.get_section(config.config_ini_section)
    
    # Determine the dialect based on the URL
    url = cfg.get("sqlalchemy.url")
    dialect = make_url(url).get_dialect().name
    print(f"Using dialect: {dialect}")
    
    # Create the engine
    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        # Force PostgreSQL dialect
        context.configure(
            connection=connection, 
            target_metadata=target_metadata,
            dialect_name="postgresql"
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
