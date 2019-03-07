from sqlalchemy import (
    Column,
    DateTime,
    func,
    String
)

from lnd_sql.database.base import Base


class Peers(Base):
    __tablename__ = 'peers'

    created_at = Column(DateTime(timezone=True),
                        nullable=False,
                        server_default=func.now())

    updated_at = Column(DateTime(timezone=True),
                        nullable=False,
                        onupdate=func.now(),
                        server_default=func.now())

    deleted_at = Column(DateTime(timezone=True),
                        nullable=True)

    pubkey = Column(String, primary_key=True)
