import csv
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.models import ETLLightningAddresses


class UpsertChannelGraph(object):
    def __init__(self, rpc: Client):
        self.rpc = rpc

    def upsert_all(self):
        channel_graph = self.rpc.describe_graph()

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLLightningAddresses.csv_columns)
        for node in channel_graph.nodes:
            for address in node.addresses:
                data: dict = MessageToDict(address)
                data['pubkey'] = node.pub_key
                data['address'] = data.pop('addr', None)
                writer.writerow(data)
        ETLLightningAddresses.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLLightningAddresses,
                                    session.connection(),
                                    ETLLightningAddresses.csv_columns,
                                    **flags)
        ETLLightningAddresses.load()
        ETLLightningAddresses.truncate()
