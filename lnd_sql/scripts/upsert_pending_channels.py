import csv
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.models import ETLPendingOpenChannels


class UpsertPendingChannels(object):
    def __init__(self, rpc: Client, local_pubkey: str):
        self.rpc = rpc
        self.local_pubkey = local_pubkey

    def upsert_all(self):
        pending_channels = self.rpc.pending_channels()

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLPendingOpenChannels.csv_columns)
        for pending_open_channel in pending_channels.pending_open_channels:
            data: dict = MessageToDict(pending_open_channel)
            nested_data = data.pop('channel')
            data.update(nested_data)
            data['local_pubkey'] = self.local_pubkey
            data['remote_pubkey'] = data.pop('remote_node_pub')
            writer.writerow(data)
        ETLPendingOpenChannels.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLPendingOpenChannels,
                                    session.connection(),
                                    ETLPendingOpenChannels.csv_columns,
                                    **flags)
        ETLPendingOpenChannels.load()
        ETLPendingOpenChannels.truncate()
