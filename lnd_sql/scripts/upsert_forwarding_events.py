from datetime import datetime

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.elements import and_

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse
from lnd_sql.database.session import session_scope
from lnd_sql.logger import log
from lnd_sql.models.forwarding_events import ForwardingEvents


class UpsertForwardingEvents(object):
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
        self.index_offset = None
        self.info: GetInfoResponse = self.rpc.get_info()

    def upsert_all(self):
        forwarding_events = self.rpc.forwarding_history(
            start_time=1,
            end_time=int(datetime.now().timestamp()),
            num_max_events=10000,
            index_offset=self.index_offset
        )
        log.debug(
            'forwarding_events',
            last_offset_index=forwarding_events.last_offset_index
        )
        self.index_offset = forwarding_events.last_offset_index
        forwarding_event_dicts = [MessageToDict(c)
                                  for c in forwarding_events.forwarding_events]
        for forwarding_event_dict in forwarding_event_dicts:
            self.upsert(self.info.identity_pubkey, forwarding_event_dict)

    @staticmethod
    def upsert(local_pubkey, data: dict):
        with session_scope() as session:
            try:
                record = (
                    session
                        .query(ForwardingEvents)
                        .filter(
                        and_(ForwardingEvents.local_pubkey == local_pubkey,
                             ForwardingEvents.timestamp == data['timestamp'])
                        )
                        .one()
                )
            except NoResultFound:
                record = ForwardingEvents()
                record.local_pubkey = local_pubkey
                record.timestamp = data['timestamp']
                session.add(record)

            for key, value in data.items():
                setattr(record, key, value)
