from sqlalchemy import (
    Column,
    DateTime,
    func,
    Integer,
    String)

from lnd_sql.database.base import Base


class Balances(Base):
    __tablename__ = 'balances'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    id = Column(Integer, primary_key=True)

    pubkey = Column(String)
    channel_balance = Column(Integer)
    channel_pending_open_balance = Column(Integer)
    wallet_total_balance = Column(Integer)
    wallet_confirmed_balance = Column(Integer)
