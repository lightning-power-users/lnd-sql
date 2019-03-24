from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    String
)

from lnd_sql.database.base import Base


class ForwardingEvents(Base):
    __tablename__ = 'forwarding_events'

    id = Column(BIGINT, primary_key=True)

    local_pubkey = Column(String)

    channel_id_in = Column(BIGINT)
    channel_id_out = Column(BIGINT)
    timestamp = Column(DateTime(timezone=True))
    amount_in = Column(BIGINT)
    amount_out = Column(BIGINT)
    fee = Column(BIGINT)
    last_index_offset = Column(BIGINT)
