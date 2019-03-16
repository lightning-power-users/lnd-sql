from sqlalchemy import (
    BIGINT,
    Boolean,
    Column,
    DateTime,
    func,
    String
)

from lnd_sql.database.base import Base


class Peers(Base):
    __tablename__ = 'peers'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    deleted_at = Column(DateTime(timezone=True),
                        nullable=True)

    id = Column(BIGINT, primary_key=True)
    remote_pubkey = Column(String)
    local_pubkey = Column(String)
    address = Column(String)
    bytes_sent = Column(BIGINT)
    bytes_recv = Column(BIGINT)
    sat_sent = Column(BIGINT)
    sat_recv = Column(BIGINT)
    inbound = Column(Boolean)
    ping_time = Column(BIGINT)
