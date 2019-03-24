from sqlalchemy import (
    BIGINT,
    Column,
    String,
    DateTime)

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLLightningNodes(Base):

    csv_columns = ('last_update', 'pubkey', 'alias', 'color')

    __tablename__ = 'etl_lightning_nodes'

    id = Column(BIGINT, primary_key=True)

    last_update = Column(DateTime(timezone=True))
    pubkey = Column(String)
    alias = Column(String)
    color = Column(String)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_lightning_nodes;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
            INSERT INTO lightning_nodes (
                  pubkey,
                  last_update,
                  alias,
                  color
                  )
                  SELECT
                      eln.pubkey,
                      eln.last_update,
                      eln.alias,
                      eln.color
                  FROM etl_lightning_nodes eln
                    LEFT OUTER JOIN lightning_nodes
                      ON eln.pubkey = lightning_nodes.pubkey
                  WHERE lightning_nodes.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM lightning_nodes 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_lightning_nodes eln
                    WHERE eln.pubkey = lightning_nodes.pubkey);
                """)
