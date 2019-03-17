from sqlalchemy import BIGINT, Column, String

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLPendingOpenChannels(Base):
    __tablename__ = 'etl_pending_open_channels'

    csv_columns = ('confirmation_height', 'commit_fee', 'commit_weight',
                   'fee_per_kw', 'remote_pubkey', 'local_pubkey',
                   'channel_point', 'capacity', 'local_balance',
                   'remote_balance')

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

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_pending_open_channels;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
        UPDATE pending_open_channels
        SET
          confirmation_height = etl_pending_open_channels.confirmation_height,
          commit_fee          = etl_pending_open_channels.commit_fee,
          commit_weight       = etl_pending_open_channels.commit_weight,
          fee_per_kw          = etl_pending_open_channels.fee_per_kw,
          remote_pubkey       = etl_pending_open_channels.remote_pubkey,
          local_pubkey        = etl_pending_open_channels.local_pubkey,
          capacity            = etl_pending_open_channels.capacity,
          local_balance       = etl_pending_open_channels.local_balance,
          remote_balance      = etl_pending_open_channels.remote_balance
        FROM etl_pending_open_channels
        WHERE etl_pending_open_channels.channel_point = pending_open_channels.channel_point
          AND etl_pending_open_channels.local_pubkey = pending_open_channels.local_pubkey;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO pending_open_channels (
                    confirmation_height,
                    commit_fee,
                    commit_weight,
                    fee_per_kw,
                    remote_pubkey,
                    local_pubkey,
                    channel_point,
                    capacity,
                    local_balance,
                    remote_balance
                  )
                  SELECT
                      epoc.confirmation_height,
                      epoc.commit_fee,
                      epoc.commit_weight,
                      epoc.fee_per_kw,
                      epoc.remote_pubkey,
                      epoc.local_pubkey,
                      epoc.channel_point,
                      epoc.capacity,
                      epoc.local_balance,
                      epoc.remote_balance
                  FROM etl_pending_open_channels epoc
                    LEFT OUTER JOIN pending_open_channels
                      ON epoc.channel_point = pending_open_channels.channel_point
                      AND epoc.local_pubkey = pending_open_channels.local_pubkey
                  WHERE pending_open_channels.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM pending_open_channels 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_pending_open_channels epoc
                    WHERE epoc.channel_point = pending_open_channels.channel_point
                    AND epoc.local_pubkey = pending_open_channels.local_pubkey);
                """)
