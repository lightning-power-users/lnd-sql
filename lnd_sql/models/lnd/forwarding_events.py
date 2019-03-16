from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    func,
    String
)

from lnd_sql.database.base import Base


class ForwardingEvents(Base):
    __tablename__ = 'forwarding_events'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    id = Column(BIGINT, primary_key=True)

    local_pubkey = Column(String)

    chan_id_in = Column(BIGINT)
    chan_id_out = Column(BIGINT)
    timestamp = Column(BIGINT)
    amt_in = Column(BIGINT)
    amt_out = Column(BIGINT)
    fee = Column(BIGINT)
    fee_msat = Column(BIGINT)
    last_offset_index = Column(BIGINT)
