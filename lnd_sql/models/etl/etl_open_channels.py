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
                   'num_updates', 'csv_delay', 'private', 'unsettled_balance')

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
    total_satoshis_received = Column(BIGINT)
    num_updates = Column(BIGINT)
    csv_delay = Column(BIGINT)
    unsettled_balance = Column(BIGINT)
    private = Column(Boolean)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_open_channels;
                    """)
