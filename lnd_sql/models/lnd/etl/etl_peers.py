from sqlalchemy import BIGINT, Boolean, Column, String

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLPeers(Base):
    __tablename__ = 'etl_peers'

    csv_columns = ('remote_pubkey', 'address', 'bytes_sent', 'bytes_recv',
                   'local_pubkey', 'sat_sent', 'sat_recv', 'inbound',
                   'ping_time')

    id = Column(BIGINT, primary_key=True)

    remote_pubkey = Column(String)
    local_pubkey = Column(String)
    address = Column(String)
    bytes_sent = Column(BIGINT)
    bytes_recv = Column(BIGINT)
    sat_sent = Column(BIGINT)
    sat_recv = Column(BIGINT)
    inbound = Column(Boolean)
    ping_time = Column(BIGINT)


    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_peers;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
        UPDATE peers
        SET
          address    = etl_peers.address,
          bytes_sent = etl_peers.bytes_sent,
          bytes_recv = etl_peers.bytes_recv,
          sat_sent   = etl_peers.sat_sent,
          sat_recv   = etl_peers.sat_recv,
          inbound    = etl_peers.inbound,
          ping_time  = etl_peers.ping_time
        FROM etl_peers
        WHERE etl_peers.remote_pubkey = peers.remote_pubkey
          AND etl_peers.local_pubkey = peers.local_pubkey;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO peers (
                  remote_pubkey,
                  local_pubkey,
                  address,
                  bytes_sent,
                  bytes_recv,
                  sat_sent,
                  sat_recv,
                  inbound,
                  ping_time
                  )
                  SELECT
                      ep.remote_pubkey,
                      ep.local_pubkey,
                      ep.address,
                      ep.bytes_sent,
                      ep.bytes_recv,
                      ep.sat_sent,
                      ep.sat_recv,
                      ep.inbound,
                      ep.ping_time
                  FROM etl_peers ep
                    LEFT OUTER JOIN peers
                      ON ep.remote_pubkey = peers.remote_pubkey
                      and ep.local_pubkey = peers.local_pubkey
                  WHERE peers.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM peers 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_peers 
                    WHERE etl_peers.remote_pubkey = peers.remote_pubkey 
                    AND etl_peers.local_pubkey = peers.local_pubkey);
                """)
