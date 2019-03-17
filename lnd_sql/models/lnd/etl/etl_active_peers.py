from sqlalchemy import BIGINT, Boolean, Column, String

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLActivePeers(Base):
    __tablename__ = 'etl_active_peers'

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
                    TRUNCATE etl_active_peers;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
        UPDATE active_peers
        SET
          address    = etl_active_peers.address,
          bytes_sent = etl_active_peers.bytes_sent,
          bytes_recv = etl_active_peers.bytes_recv,
          sat_sent   = etl_active_peers.sat_sent,
          sat_recv   = etl_active_peers.sat_recv,
          inbound    = etl_active_peers.inbound,
          ping_time  = etl_active_peers.ping_time
        FROM etl_active_peers
        WHERE etl_active_peers.remote_pubkey = active_peers.remote_pubkey
          AND etl_active_peers.local_pubkey = active_peers.local_pubkey;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO active_peers (
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
                      eap.remote_pubkey,
                      eap.local_pubkey,
                      eap.address,
                      eap.bytes_sent,
                      eap.bytes_recv,
                      eap.sat_sent,
                      eap.sat_recv,
                      eap.inbound,
                      eap.ping_time
                  FROM etl_active_peers eap
                    LEFT OUTER JOIN active_peers
                      ON eap.remote_pubkey = active_peers.remote_pubkey
                      and eap.local_pubkey = active_peers.local_pubkey
                  WHERE active_peers.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM active_peers 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_active_peers 
                    WHERE etl_active_peers.remote_pubkey = active_peers.remote_pubkey 
                    AND etl_active_peers.local_pubkey = active_peers.local_pubkey);
                """)
