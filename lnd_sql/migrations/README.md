### Creating a migration
alembic --config lnd_sql/migrations/alembic.ini revision --autogenerate -m "Revision description"


### Migrating
alembic --config lnd_sql/migrations/alembic.ini upgrade head