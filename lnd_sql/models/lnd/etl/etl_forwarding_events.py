from sqlalchemy import BIGINT, Column, DateTime, String

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLForwardingEvents(Base):
    __tablename__ = 'etl_forwarding_events'

    csv_columns = (
        'channel_id_in', 'channel_id_out', 'timestamp', 'amount_in',
        'amount_out', 'fee', 'last_index_offset', 'local_pubkey'
    )

    id = Column(BIGINT, primary_key=True)

    local_pubkey = Column(String)

    channel_id_in = Column(BIGINT)
    channel_id_out = Column(BIGINT)
    timestamp = Column(DateTime(timezone=True))
    amount_in = Column(BIGINT)
    amount_out = Column(BIGINT)
    fee = Column(BIGINT)
    last_index_offset = Column(BIGINT)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_forwarding_events;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
            INSERT INTO forwarding_events (
                  channel_id_in,
                  channel_id_out,
                  timestamp,
                  amount_in,
                  amount_out,
                  fee,
                  local_pubkey,
                  last_index_offset
                  )
                  SELECT
                      efe.channel_id_in,
                      efe.channel_id_out,
                      efe.timestamp,
                      efe.amount_in,
                      efe.amount_out,
                      efe.fee,
                      efe.local_pubkey,
                      efe.last_index_offset
                  FROM etl_forwarding_events efe
                    LEFT OUTER JOIN forwarding_events
                      ON efe.timestamp = forwarding_events.timestamp
                      AND efe.channel_id_out = forwarding_events.channel_id_out
                      AND efe.channel_id_in = forwarding_events.channel_id_in
                      AND efe.local_pubkey = forwarding_events.local_pubkey
                  WHERE forwarding_events.id IS NULL;
            """)
