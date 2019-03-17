from sqlalchemy import Column, DECIMAL, DateTime, Integer

from lnd_sql.database.base import Base


class ExchangeRates(Base):
    __tablename__ = 'exchange_rates'

    id = Column(Integer, primary_key=True)

    timestamp = Column(DateTime(timezone=True))
    last = Column(DECIMAL)
