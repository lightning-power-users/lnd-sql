from sqlalchemy import BIGINT, Boolean, Column, String, DateTime

from lnd_sql import session_scope
from lnd_sql.database.base import Base


class ETLInvoices(Base):
    __tablename__ = 'etl_invoices'

    csv_columns = (
        'memo', 'r_preimage', 'r_hash', 'value', 'creation_date',
        'payment_request', 'expiry', 'cltv_expiry', 'add_index', 'local_pubkey',
        'description_hash', 'settle_date', 'settled', 'amt_paid_sat',
        'settle_index', 'private', 'last_index_offset')

    id = Column(BIGINT, primary_key=True)

    local_pubkey = Column(String)
    r_hash = Column(String)
    memo = Column(String)
    r_preimage = Column(String)
    value = Column(BIGINT)
    settled = Column(Boolean)
    creation_date = Column(DateTime(timezone=True))
    settle_date = Column(DateTime(timezone=True))
    payment_request = Column(String)
    description_hash = Column(String)
    description = Column(String)
    expiry = Column(BIGINT)
    fallback_addr = Column(String)
    cltv_expiry = Column(BIGINT)
    private = Column(Boolean)
    add_index = Column(BIGINT)
    settle_index = Column(BIGINT)
    amt_paid_sat = Column(BIGINT)
    last_index_offset = Column(BIGINT)

    @classmethod
    def truncate(cls):
        with session_scope() as session:
            session.execute("""
                    TRUNCATE etl_invoices;
                    """)

    @classmethod
    def load(cls):
        # Insert any missing peers to avoid having a foreign key missing
        with session_scope() as session:
            session.execute("""
            INSERT INTO peers (pubkey) 
            SELECT DISTINCT local_pubkey
            FROM etl_invoices
              LEFT OUTER JOIN peers
                ON etl_invoices.local_pubkey = peers.pubkey
              WHERE peers.pubkey IS NULL;
            """)

        with session_scope() as session:
            session.execute("""
        UPDATE invoices
        SET
          add_index        = etl_invoices.add_index,
          amt_paid_sat     = etl_invoices.amt_paid_sat,
          cltv_expiry      = etl_invoices.cltv_expiry,
          creation_date    = etl_invoices.creation_date,
          description_hash = etl_invoices.description_hash,
          expiry           = etl_invoices.expiry,
          fallback_addr    = etl_invoices.fallback_addr,
          local_pubkey     = etl_invoices.local_pubkey,
          memo             = etl_invoices.memo,
          payment_request  = etl_invoices.payment_request,
          private          = etl_invoices.private,
          r_preimage       = etl_invoices.r_preimage,
          settle_date      = etl_invoices.settle_date,
          settle_index     = etl_invoices.settle_index,
          settled          = etl_invoices.settled,
          value            = etl_invoices.value
        FROM etl_invoices
        WHERE etl_invoices.r_hash = invoices.r_hash;
            """)

        with session_scope() as session:
            session.execute("""
            INSERT INTO invoices (
                  r_hash,
                  memo,
                  r_preimage,
                  value,
                  settled,
                  creation_date,
                  settle_date,
                  payment_request,
                  description_hash,
                  description,
                  expiry,
                  fallback_addr,
                  cltv_expiry,
                  private,
                  add_index,
                  settle_index,
                  amt_paid_sat,
                  local_pubkey
                  )
                  SELECT
                      ei.r_hash,
                      ei.memo,
                      ei.r_preimage,
                      ei.value,
                      ei.settled,
                      ei.creation_date,
                      ei.settle_date,
                      ei.payment_request,
                      ei.description_hash,
                      ei.description,
                      ei.expiry,
                      ei.fallback_addr,
                      ei.cltv_expiry,
                      ei.private,
                      ei.add_index,
                      ei.settle_index,
                      ei.amt_paid_sat,
                      ei.local_pubkey
                  FROM etl_invoices ei
                    LEFT OUTER JOIN invoices
                      ON ei.r_hash = invoices.r_hash
                  WHERE invoices.r_hash IS NULL;
            """)
