from sqlalchemy import (
    BIGINT,
    DECIMAL,
    Column,
    DateTime,
    func,
    String
)

from lnd_sql.database.base import Base


class SmartFeeEstimates(Base):
    __tablename__ = 'smart_fee_estimates'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    id = Column(BIGINT, primary_key=True)

    conf_target = Column(BIGINT)
    label = Column(String)
    fee_rate = Column(DECIMAL)
