from sqlalchemy import (
    BIGINT,
    Column,
    String
)

from lnd_sql.database.base import Base


class LightningAddresses(Base):
    __tablename__ = 'lightning_addresses'

    id = Column(BIGINT, primary_key=True)

    pubkey = Column(String)
    network = Column(String)
    address = Column(String)
