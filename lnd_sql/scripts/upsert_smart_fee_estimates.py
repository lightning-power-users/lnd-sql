import csv
from io import StringIO

# noinspection PyPackageRequirements
import postgres_copy

from bitcoin.rpc import Proxy

from lnd_sql.database.session import session_scope
from lnd_sql.models import ETLSmartFeeEstimates


class UpsertSmartFeeEstimates(object):
    @staticmethod
    def estimate_smart_fee(conf_target, mode):
        # noinspection PyProtectedMember
        r = Proxy()._call('estimatesmartfee', conf_target, mode)
        return r

    def upsert_all(self):
        fee_estimates = [
            dict(conf_target=1, label='Ten minutes'),
            dict(conf_target=6, label='One_hour'),
            dict(conf_target=36, label='Six hours'),
            dict(conf_target=72, label='Twelve hours'),
            dict(conf_target=144, label='One day'),
            dict(conf_target=288, label='Two days'),
            dict(conf_target=432, label='Three days'),
            dict(conf_target=1008, label='One week')
        ]

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLSmartFeeEstimates.csv_columns)

        for fee_estimate in fee_estimates:
            # noinspection PyProtectedMember
            fee_estimate['fee_rate'] = self.estimate_smart_fee(
                fee_estimate['conf_target'],
                'ECONOMICAL'
            )['feerate']
            writer.writerow(fee_estimate)
        ETLSmartFeeEstimates.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLSmartFeeEstimates,
                                    session.connection(),
                                    ETLSmartFeeEstimates.csv_columns,
                                    **flags)
        ETLSmartFeeEstimates.load()
        ETLSmartFeeEstimates.truncate()
