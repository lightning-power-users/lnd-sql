from sqlalchemy import func

from lnd_sql.database.session import session_scope
from lnd_sql.models import OpenChannels
from lnd_sql.logger import log


class BalanceSheet(object):
    def __init__(self):
        with session_scope() as session:
            prepaid_commit_fee = (
                session.query(func.sum(OpenChannels.commit_fee)).scalar()
            )
            channel_balance = (
                session.query(func.sum(OpenChannels.local_balance)).scalar()
            )
            total_assets = channel_balance + prepaid_commit_fee
            log.info('assets',
                     prepaid_commit_fee=prepaid_commit_fee,
                     channel_balance=channel_balance,
                     total_assets=total_assets)


if __name__ == '__main__':
    BalanceSheet()
