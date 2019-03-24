from sqlalchemy import BIGINT, Boolean, Column, String

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLOpenChannels(Base):
    __tablename__ = 'etl_open_channels'

    csv_columns = ('chan_id', 'active', 'local_pubkey',
                   'remote_pubkey', 'channel_point',
                   'capacity', 'local_balance', 'remote_balance',
                   'commit_fee', 'commit_weight', 'fee_per_kw',
                   'total_satoshis_sent', 'total_satoshis_received',
                   'num_updates', 'csv_delay', 'private', 'unsettled_balance',
                   'initiator')

    id = Column(BIGINT, primary_key=True)

    chan_id = Column(BIGINT)
    active = Column(Boolean)
    local_pubkey = Column(String)
    remote_pubkey = Column(String)
    channel_point = Column(String)
    capacity = Column(BIGINT, nullable=False, server_default='0')
    local_balance = Column(BIGINT, nullable=False, server_default='0')
    remote_balance = Column(BIGINT, nullable=False, server_default='0')
    commit_fee = Column(BIGINT)
    commit_weight = Column(BIGINT)
    fee_per_kw = Column(BIGINT)
    total_satoshis_sent = Column(BIGINT, nullable=False, server_default='0')
    total_satoshis_received = Column(BIGINT, nullable=False, server_default='0')
    num_updates = Column(BIGINT)
    csv_delay = Column(BIGINT)
    private = Column(Boolean)
    unsettled_balance = Column(BIGINT, nullable=False, server_default='0')
    initiator = Column(Boolean)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_open_channels;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
        UPDATE open_channels
        SET
          active                  = etl_open_channels.active,
          capacity                = etl_open_channels.capacity,
          commit_fee              = etl_open_channels.commit_fee,
          commit_weight           = etl_open_channels.commit_weight,
          csv_delay               = etl_open_channels.csv_delay,
          fee_per_kw              = etl_open_channels.fee_per_kw,
          local_balance           = etl_open_channels.local_balance,
          num_updates             = etl_open_channels.num_updates,
          private                 = etl_open_channels.private,
          remote_balance          = etl_open_channels.remote_balance,
          total_satoshis_received = etl_open_channels.total_satoshis_received,
          total_satoshis_sent     = etl_open_channels.total_satoshis_sent,
          unsettled_balance       = etl_open_channels.unsettled_balance,
          initiator               = etl_open_channels.initiator
        FROM etl_open_channels
        WHERE etl_open_channels.chan_id = open_channels.chan_id
          AND etl_open_channels.local_pubkey = open_channels.local_pubkey;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO open_channels (
                  active,
                  capacity,
                  chan_id,
                  channel_point,
                  commit_fee,
                  commit_weight,
                  csv_delay,
                  fee_per_kw,
                  local_balance,
                  local_pubkey,
                  num_updates,
                  private,
                  remote_balance,
                  remote_pubkey,
                  total_satoshis_received,
                  total_satoshis_sent,
                  unsettled_balance,
                  initiator
                  )
                  SELECT
                      eoc.active,
                      eoc.capacity,
                      eoc.chan_id,
                      eoc.channel_point,
                      eoc.commit_fee,
                      eoc.commit_weight,
                      eoc.csv_delay,
                      eoc.fee_per_kw,
                      eoc.local_balance,
                      eoc.local_pubkey,
                      eoc.num_updates,
                      eoc.private,
                      eoc.remote_balance,
                      eoc.remote_pubkey,
                      eoc.total_satoshis_received,
                      eoc.total_satoshis_sent,
                      eoc.unsettled_balance,
                      eoc.initiator
                  FROM etl_open_channels eoc
                    LEFT OUTER JOIN open_channels
                      ON eoc.chan_id = open_channels.chan_id
                      and eoc.local_pubkey = open_channels.local_pubkey
                  WHERE open_channels.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM open_channels 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_open_channels 
                    WHERE etl_open_channels.chan_id = open_channels.chan_id);
                """)
