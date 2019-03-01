from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    func,
    String,
    Boolean)
from sqlalchemy.orm import Session

from lnd_sql.database.session import session_scope
from lnd_sql.database.base import Base


class OpenChannels(Base):
    __tablename__ = 'open_channels'

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

    chan_id = Column(BIGINT)
    active = Column(Boolean)
    local_pubkey = Column(String)
    remote_pubkey = Column(String)
    channel_point = Column(String)
    capacity = Column(BIGINT)
    local_balance = Column(BIGINT)
    remote_balance = Column(BIGINT)
    commit_fee = Column(BIGINT)
    commit_weight = Column(BIGINT)
    fee_per_kw = Column(BIGINT)
    total_satoshis_sent = Column(BIGINT)
    num_updates = Column(BIGINT)
    csv_delay = Column(BIGINT)


if __name__ == '__main__':
    session: Session = None
    with session_scope() as session:
        Base.metadata.create_all(session.get_bind())
