from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context
from dotenv import load_dotenv
import os


# internal imports:
from db.schema import Base

load_dotenv()


database_url = os.getenv("DATABASE_URL")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
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


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    connectable = create_engine(database_url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            on_version_apply=on_version_apply,
        )

        with context.begin_transaction():
            context.run_migrations()


def on_version_apply(revision, context):
    migration_module = revision.module

    # Check if the 'table_changed' flag is set
    if getattr(migration_module, "table_changed", False):
        # Call your update function
        update_menu_mapping()


def update_menu_mapping(table_name, mapping_file_path, column_renames=None):
    """
    Updates the mapping file based on the current schema of the specified table.

    :param table_name: Name of the database table.
    :param mapping_file_path: Path to the mapping file (e.g., JSON).
    :param column_renames: Dictionary mapping old column names to new column names.
    """
    from sqlalchemy import MetaData
    import json
    from alembic import op

    # Reflect the updated schema
    bind = op.get_bind()
    metadata = MetaData()
    metadata.reflect(bind=bind, only=[table_name])
    table = metadata.tables[table_name]

    # Get the updated list of database columns
    db_columns = set(column.name for column in table.columns)

    # Load the existing mapping
    with open(mapping_file_path, "r") as f:
        mapping = json.load(f)

    # Update the mapping values based on column renames
    if column_renames:
        updated_mapping = {}
        for csv_header, db_column in mapping.items():
            if db_column in column_renames:
                # Update to the new column name
                updated_mapping[csv_header] = column_renames[db_column]
            else:
                # Keep the existing column name
                updated_mapping[csv_header] = db_column
    else:
        updated_mapping = mapping

    # Save the updated mapping
    with open(mapping_file_path, "w") as f:
        json.dump(updated_mapping, f, indent=4)


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
