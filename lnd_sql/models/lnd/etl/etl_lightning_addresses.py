from sqlalchemy import (
    BIGINT,
    Column,
    String
)

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLLightningAddresses(Base):

    csv_columns = ('pubkey', 'network', 'address')

    __tablename__ = 'etl_lightning_addresses'

    id = Column(BIGINT, primary_key=True)

    pubkey = Column(String)
    network = Column(String)
    address = Column(String)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_lightning_addresses;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
            INSERT INTO lightning_addresses (
                  pubkey,
                  network,
                  address
                  )
                  SELECT
                      ela.pubkey,
                      ela.network,
                      ela.address
                  FROM etl_lightning_addresses ela
                    LEFT OUTER JOIN lightning_addresses
                      ON ela.pubkey = lightning_addresses.pubkey
                      and ela.address = lightning_addresses.address
                  WHERE lightning_addresses.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM lightning_addresses 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_lightning_addresses ela
                    WHERE ela.pubkey = lightning_addresses.pubkey
                      and ela.address = lightning_addresses.address);
                """)
