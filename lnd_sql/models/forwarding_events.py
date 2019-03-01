from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    func,
    String
)
from sqlalchemy.orm import Session

from lnd_sql.database.session import session_scope
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


if __name__ == '__main__':
    session: Session = None
    with session_scope() as session:
        Base.metadata.create_all(session.get_bind())
