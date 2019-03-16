import csv
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.models import ETLActivePeers


class UpsertPeers(object):
    def __init__(self, rpc: Client, local_pubkey: str):
        self.rpc = rpc
        self.local_pubkey = local_pubkey

    def upsert_all(self):
        peers = self.rpc.list_peers()

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file, fieldnames=ETLActivePeers.csv_columns)
        for peer in peers:
            peer_data = MessageToDict(peer)
            peer_data['local_pubkey'] = self.local_pubkey
            peer_data['remote_pubkey'] = peer.pub_key
            peer_data.pop('pub_key', None)
            writer.writerow(peer_data)
        ETLActivePeers.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLActivePeers,
                                    session.connection(),
                                    ETLActivePeers.csv_columns,
                                    **flags)
        ETLActivePeers.load()
        ETLActivePeers.truncate()
