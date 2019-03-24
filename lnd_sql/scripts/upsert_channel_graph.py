import csv
from datetime import datetime
from io import StringIO

# noinspection PyPackageRequirements
import pytz
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.models import ETLLightningAddresses, ETLLightningNodes


class UpsertChannelGraph(object):
    def __init__(self, rpc: Client):
        self.rpc = rpc

    def upsert_all(self):
        channel_graph = self.rpc.describe_graph()
        self.upsert_lightning_addresses(channel_graph)
        self.upsert_lightning_nodes(channel_graph)

    @staticmethod
    def upsert_lightning_addresses(channel_graph):
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

    @staticmethod
    def upsert_lightning_nodes(channel_graph):
        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLLightningNodes.csv_columns)
        for node in channel_graph.nodes:
            data: dict = MessageToDict(node)
            data.pop('addresses', None)
            data['pubkey'] = data.pop('pub_key')
            data['last_update'] = datetime.utcfromtimestamp(
                node.last_update).replace(tzinfo=pytz.utc)
            writer.writerow(data)
        ETLLightningNodes.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLLightningNodes,
                                    session.connection(),
                                    ETLLightningNodes.csv_columns,
                                    **flags)
        ETLLightningNodes.load()
        ETLLightningNodes.truncate()

    # @staticmethod
    # def upsert_channel_edges(channel_graph):
    #     csv_file = StringIO()
    #     writer = csv.DictWriter(csv_file,
    #                             fieldnames=ETLChannelEdges.csv_columns)
    #     for node in channel_graph.nodes:
    #         data: dict = MessageToDict(node)
    #         data.pop('addresses')
    #         data['pubkey'] = node.pub_key
    #
    #         data['last_update'] = datetime.utcfromtimestamp(
    #             node.last_update).replace(tzinfo=pytz.utc)
    #         writer.writerow(data)
    #     ETLChannelEdges.truncate()
    #     flags = {'format': 'csv', 'header': False}
    #     with session_scope() as session:
    #         csv_file.seek(0)
    #         postgres_copy.copy_from(csv_file,
    #                                 ETLChannelEdges,
    #                                 session.connection(),
    #                                 ETLChannelEdges.csv_columns,
    #                                 **flags)
    #     ETLChannelEdges.load()
    #     ETLChannelEdges.truncate()
    #
    #
    # @staticmethod
    # def upsert_routing_policies(channel_graph):
    #     csv_file = StringIO()
    #     writer = csv.DictWriter(csv_file,
    #                             fieldnames=ETLRoutingPolicies.csv_columns)
    #     for node in channel_graph.nodes:
    #         data: dict = MessageToDict(node)
    #         data.pop('addresses')
    #         data['pubkey'] = node.pub_key
    #
    #         data['last_update'] = datetime.utcfromtimestamp(
    #             node.last_update).replace(tzinfo=pytz.utc)
    #         writer.writerow(data)
    #     ETLRoutingPolicies.truncate()
    #     flags = {'format': 'csv', 'header': False}
    #     with session_scope() as session:
    #         csv_file.seek(0)
    #         postgres_copy.copy_from(csv_file,
    #                                 ETLRoutingPolicies,
    #                                 session.connection(),
    #                                 ETLRoutingPolicies.csv_columns,
    #                                 **flags)
    #     ETLRoutingPolicies.load()
    #     ETLRoutingPolicies.truncate()
