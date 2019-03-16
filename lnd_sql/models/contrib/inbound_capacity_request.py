from sqlalchemy import (
    BIGINT,
    Column,
    DateTime,
    ForeignKey,
    func,
    Integer,
    Numeric,
    String
)

from lnd_sql.database.base import Base
from lnd_sql.models.lnd.invoices import Invoices


class InboundCapacityRequest(Base):
    __tablename__ = 'inbound_capacity_request'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    deleted_at = Column(DateTime(timezone=True),
                        nullable=True)

    id = Column(Integer, primary_key=True)

    invoice_r_hash = Column(String, ForeignKey(Invoices.r_hash))

    session_id = Column(String)
    remote_pubkey = Column(String)
    remote_host = Column(String)

    capacity = Column(BIGINT)
    # As percentage of capacity
    capacity_fee_rate = Column(Numeric)
    capacity_fee = Column(BIGINT)
    # As sats per byte
    transaction_fee_rate = Column(BIGINT)
    expected_bytes = Column(BIGINT)
    transaction_fee = Column(BIGINT)
    total_fee = Column(BIGINT)

    keep_open_until = Column(DateTime(timezone=True))
