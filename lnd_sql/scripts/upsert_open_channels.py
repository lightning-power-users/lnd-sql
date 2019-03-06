import csv
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse
from lnd_sql.database.session import session_scope
from lnd_sql.models.etl.etl_open_channels import ETLOpenChannels


class UpsertOpenChannels(object):
    rpc: Client

    def __init__(self,
                 tls_cert_path: str = None,
                 macaroon_path: str = None,
                 lnd_network: str = 'mainnet',
                 lnd_grpc_host: str = '127.0.0.1',
                 lnd_grpc_port: str = '10009'):
        self.rpc = Client(
            tls_cert_path=tls_cert_path,
            macaroon_path=macaroon_path,
            network=lnd_network,
            grpc_host=lnd_grpc_host,
            grpc_port=lnd_grpc_port,
        )

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
