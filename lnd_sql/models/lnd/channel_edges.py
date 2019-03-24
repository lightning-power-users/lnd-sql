from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    String
)

from lnd_sql.database.base import Base


class ChannelEdges(Base):
    __tablename__ = 'channel_edges'

    id = Column(BIGINT, primary_key=True)

    channel_id = Column(BIGINT)
    last_update = Column(DateTime(timezone=True))
    node1_pubkey = Column(String)
    node2_pubkey = Column(String)
    chan_point = Column(String)
    capacity = Column(BIGINT)
