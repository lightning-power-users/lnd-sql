from sqlalchemy import (
    BIGINT,
    Boolean,
    Column,
    DateTime,
    String
)

from lnd_sql.database.base import Base


class Invoices(Base):
    __tablename__ = 'invoices'

    r_hash = Column(String, primary_key=True)
    memo = Column(String)
    r_preimage = Column(String)
    value = Column(BIGINT)
    settled = Column(Boolean)
    creation_date = Column(DateTime(timezone=True))
    settle_date = Column(DateTime(timezone=True))
    payment_request = Column(String)
    description_hash = Column(String)
    description = Column(String)
    expiry = Column(BIGINT)
    fallback_addr = Column(String)
    cltv_expiry = Column(BIGINT)
    private = Column(Boolean)
    add_index = Column(BIGINT)
    settle_index = Column(BIGINT)
    amt_paid = Column(BIGINT)
    amt_paid_sat = Column(BIGINT)
    amt_paid_msat = Column(BIGINT)
    invoice_state = Column(String)
