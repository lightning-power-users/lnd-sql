from sqlalchemy import (
    BIGINT,
    Column,
    String,
    DateTime)

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLChannelEdges(Base):

    csv_columns = ('channel_id', 'chan_point', 'last_update', 'node1_pubkey',
                   'node2_pubkey', 'capacity')

    __tablename__ = 'etl_channel_edges'

    id = Column(BIGINT, primary_key=True)

    channel_id = Column(BIGINT)
    last_update = Column(DateTime(timezone=True))
    node1_pubkey = Column(String)
    node2_pubkey = Column(String)
    chan_point = Column(String)
    capacity = Column(BIGINT)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_channel_edges;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
            INSERT INTO channel_edges (
                  channel_id,
                  last_update,
                  node1_pubkey,
                  node2_pubkey,
                  chan_point,
                  capacity
                  )
                  SELECT
                      ece.channel_id,
                      ece.last_update,
                      ece.node1_pubkey,
                      ece.node2_pubkey,
                      ece.chan_point,
                      ece.capacity
                  FROM etl_channel_edges ece
                    LEFT OUTER JOIN channel_edges
                      ON ece.channel_id = channel_edges.channel_id
                  WHERE channel_edges.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM channel_edges 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_channel_edges ece
                    WHERE ece.channel_id = channel_edges.channel_id);
                """)
