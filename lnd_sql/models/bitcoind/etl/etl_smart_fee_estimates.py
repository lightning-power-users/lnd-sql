from sqlalchemy import BIGINT, Column, String, DECIMAL

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLSmartFeeEstimates(Base):
    __tablename__ = 'etl_smart_fee_estimates'

    csv_columns = ('conf_target', 'label', 'fee_rate')

    id = Column(BIGINT, primary_key=True)

    conf_target = Column(BIGINT)
    label = Column(String)
    fee_rate = Column(DECIMAL)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_smart_fee_estimates;
                    """)

    @classmethod
    def load(cls):
        with session_scope() as session:
            session.execute("""
        UPDATE smart_fee_estimates
        SET
          fee_rate                  = etl_smart_fee_estimates.fee_rate
        FROM etl_smart_fee_estimates
        WHERE etl_smart_fee_estimates.conf_target = smart_fee_estimates.conf_target;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO smart_fee_estimates (
                    conf_target,
                    label,
                    fee_rate
                  )
                  SELECT
                      esfe.conf_target,
                      esfe.label,
                      esfe.fee_rate
                  FROM etl_smart_fee_estimates esfe
                    LEFT OUTER JOIN smart_fee_estimates
                      ON esfe.conf_target = smart_fee_estimates.conf_target
                  WHERE smart_fee_estimates.id IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
                DELETE FROM smart_fee_estimates 
                WHERE NOT EXISTS (
                    SELECT 1 FROM etl_smart_fee_estimates 
                    WHERE etl_smart_fee_estimates.conf_target = smart_fee_estimates.conf_target);
                """)
