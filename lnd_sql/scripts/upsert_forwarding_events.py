from datetime import datetime

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
from sqlalchemy import func
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.sql.elements import and_

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.logger import log
from lnd_sql.models.lnd import ForwardingEvents


class UpsertForwardingEvents(object):
    def __init__(self, rpc: Client, local_pubkey: str):
        self.rpc = rpc
        self.local_pubkey = local_pubkey

    @staticmethod
    def get_last_offset_index() -> int:
        with session_scope() as session:
            record = (
                session
                .query(func.max(ForwardingEvents.last_offset_index))
                .scalar()
            )
            return record

    def upsert_all(self):
        forwarding_events = self.rpc.forwarding_history(
            start_time=1,
            end_time=int(datetime.now().timestamp()),
            num_max_events=10000,
            index_offset=self.get_last_offset_index()
        )
        log.debug(
            'forwarding_events',
            last_offset_index=forwarding_events.last_offset_index
        )
        forwarding_event_dicts = [MessageToDict(c)
                                  for c in forwarding_events.forwarding_events]
        for item in forwarding_event_dicts:
            item.update(
                {'last_offset_index': forwarding_events.last_offset_index}
            )
        for forwarding_event_dict in forwarding_event_dicts:
            self.upsert(self.local_pubkey, forwarding_event_dict)

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
