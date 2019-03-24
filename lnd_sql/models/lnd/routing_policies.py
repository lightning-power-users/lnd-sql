from sqlalchemy import (
    BIGINT,
    Boolean,
    Column,
    DateTime,
    String
)

from lnd_sql.database.base import Base


class RoutingPolicies(Base):

    csv_columns = ('pubkey', 'channel_id', 'last_update', 'time_lock_delta',
                   'min_htlc', 'fee_base_msat', 'fee_rate_milli_msat',
                   'disabled', 'max_htlc_msat')

    __tablename__ = 'routing_policies'

    id = Column(BIGINT, primary_key=True)

    pubkey = Column(String)
    channel_id = Column(BIGINT)
    last_update = Column(DateTime(timezone=True))
    time_lock_delta = Column(BIGINT)
    min_htlc = Column(BIGINT)
    fee_base_msat = Column(BIGINT)
    fee_rate_milli_msat = Column(BIGINT)
    disabled = Column(Boolean)
    max_htlc_msat = Column(BIGINT)
