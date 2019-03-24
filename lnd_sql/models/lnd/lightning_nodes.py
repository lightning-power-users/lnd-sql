from sqlalchemy import (
    BIGINT,
    Column,
    String,
    DateTime)

from lnd_sql.database.base import Base


class LightningNodes(Base):
    __tablename__ = 'lightning_nodes'

    id = Column(BIGINT, primary_key=True)

    last_update = Column(DateTime(timezone=True))
    pubkey = Column(String)
    alias = Column(String)
    color = Column(String)
