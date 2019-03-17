from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    func,
    String
)

from lnd_sql.database.base import Base


class PendingOpenChannels(Base):
    __tablename__ = 'pending_open_channels'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    id = Column(BIGINT, primary_key=True)

    confirmation_height = Column(BIGINT)
    commit_fee = Column(BIGINT)
    commit_weight = Column(BIGINT)
    fee_per_kw = Column(BIGINT)
    remote_pubkey = Column(String)
    local_pubkey = Column(String)
    channel_point = Column(String)
    capacity = Column(BIGINT)
    local_balance = Column(BIGINT)
    remote_balance = Column(BIGINT)

