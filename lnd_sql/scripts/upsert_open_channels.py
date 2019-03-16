import csv
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse
from lnd_sql.database.session import session_scope
from lnd_sql.models.lnd import ETLOpenChannels


class UpsertOpenChannels(object):
    def __init__(self, rpc: Client, local_pubkey: str):
        self.rpc = rpc
        self.local_pubkey = local_pubkey

    def upsert_all(self):
        channels = self.rpc.list_channels()
        info: GetInfoResponse = self.rpc.get_info()

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLOpenChannels.csv_columns)
        channel_dicts = [MessageToDict(c) for c in channels]
        for channel_dict in channel_dicts:
            channel_dict['local_pubkey'] = info.identity_pubkey
            channel_dict.pop('pending_htlcs', None)
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
