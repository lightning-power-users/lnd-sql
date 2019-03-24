from sqlalchemy import (
    BIGINT,
    Column,
    String,
    DateTime, Boolean)

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLRoutingPolicies(Base):

    csv_columns = ('pubkey', 'channel_id', 'last_update', 'time_lock_delta',
                   'min_htlc', 'fee_base_msat', 'fee_rate_milli_msat',
                   'disabled', 'max_htlc_msat')

    __tablename__ = 'etl_routing_policies'

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

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_routing_policies;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
        UPDATE routing_policies
        SET
            last_update         = erp.last_update,
            time_lock_delta     = erp.time_lock_delta,
            min_htlc            = erp.min_htlc,
            fee_base_msat       = erp.fee_base_msat,
            fee_rate_milli_msat = erp.fee_rate_milli_msat,
            disabled            = erp.disabled,
            max_htlc_msat       = erp.max_htlc_msat
        FROM etl_routing_policies erp
        WHERE erp.channel_id = routing_policies.channel_id
          AND erp.pubkey = routing_policies.pubkey;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO routing_policies (
                  pubkey,
                  last_update,
                  channel_id,
                  time_lock_delta,
                  min_htlc,
                  fee_base_msat,
                  fee_rate_milli_msat,
                  disabled,
                  max_htlc_msat
                  )
                  SELECT
                      erp.pubkey,
                      erp.last_update,
                      erp.channel_id,
                      erp.time_lock_delta,
                      erp.min_htlc,
                      erp.fee_base_msat,
                      erp.fee_rate_milli_msat,
                      erp.disabled,
                      erp.max_htlc_msat
                  FROM etl_routing_policies erp
                    LEFT OUTER JOIN routing_policies
                      ON erp.pubkey = routing_policies.pubkey
                  WHERE routing_policies.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM routing_policies 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_routing_policies erp
                    WHERE erp.pubkey = routing_policies.pubkey);
                """)
