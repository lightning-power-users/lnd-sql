import os

from alembic.config import Config
from alembic import command

from lnd_sql.database.session import session_scope
from lnd_sql.database.base import Base


def create_database(echo=True):
    with session_scope(echo=echo) as session:
        Base.metadata.create_all(session.connection())

    file_path = os.path.realpath(__file__)
    app_path = os.path.dirname(os.path.dirname(file_path))
    config_path = os.path.join(app_path, 'migrations', 'alembic.ini')

    alembic_config = Config(config_path)
    command.stamp(alembic_config, 'head')


def drop_database(echo=True):
    with session_scope(echo=echo) as session:
        Base.metadata.drop_all(session.connection())


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Change the schema')

    parser.add_argument('-d',
                        dest='drop',
                        type=bool,
                        default=False
                        )
    args = parser.parse_args()
    if args.drop:
        drop_database()
    create_database()
