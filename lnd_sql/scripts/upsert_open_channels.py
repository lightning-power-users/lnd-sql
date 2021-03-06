import csv
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.models.lnd import ETLOpenChannels


class UpsertOpenChannels(object):
    def __init__(self, rpc: Client, local_pubkey: str):
        self.rpc = rpc
        self.local_pubkey = local_pubkey

    def upsert_all(self):
        channels = self.rpc.list_channels()

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLOpenChannels.csv_columns)
        channel_dicts = [MessageToDict(c) for c in channels]
        for channel_dict in channel_dicts:
            channel_dict['local_pubkey'] = self.local_pubkey
            channel_dict.pop('pending_htlcs', None)
            channel_dict['capacity'] = channel_dict.get('capacity', 0)
            channel_dict['local_balance'] = channel_dict.get('local_balance', 0)
            channel_dict['remote_balance'] = channel_dict.get('remote_balance', 0)
            channel_dict['total_satoshis_sent'] = channel_dict.get('total_satoshis_sent', 0)
            channel_dict['total_satoshis_received'] = channel_dict.get('total_satoshis_received', 0)
            channel_dict['unsettled_balance'] = channel_dict.get('unsettled_balance', 0)
            writer.writerow(channel_dict)
        ETLOpenChannels.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLOpenChannels,
                                    session.connection(),
                                    ETLOpenChannels.csv_columns,
                                    **flags)
        ETLOpenChannels.load()
        ETLOpenChannels.truncate()
