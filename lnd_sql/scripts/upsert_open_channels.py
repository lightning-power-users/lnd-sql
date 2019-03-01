# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.elements import and_

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse
from lnd_sql.database.session import session_scope
from lnd_sql.models.open_channels import OpenChannels


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
        channel_dicts = [MessageToDict(c) for c in channels]
        for channel_dict in channel_dicts:
            self.upsert(info.identity_pubkey, channel_dict)

    @staticmethod
    def upsert(local_pubkey, data: dict):
        with session_scope() as session:
            try:
                record = (
                    session
                        .query(OpenChannels)
                        .filter(and_(OpenChannels.local_pubkey == local_pubkey,
                                     OpenChannels.chan_id == data['chan_id'])
                                )
                        .one()
                )
            except NoResultFound:
                record = OpenChannels()
                record.local_pubkey = local_pubkey
                record.chan_id = data['chan_id']
                session.add(record)

            for key, value in data.items():
                setattr(record, key, value)
