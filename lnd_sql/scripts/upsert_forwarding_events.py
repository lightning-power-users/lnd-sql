from csv import DictWriter
from datetime import datetime
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy
import pytz
from sqlalchemy import func

from lnd_grpc.lnd_grpc import Client
from lnd_sql.database.session import session_scope
from lnd_sql.logger import log
from lnd_sql.models import ETLForwardingEvents
from lnd_sql.models.lnd import ForwardingEvents


class UpsertForwardingEvents(object):
    def __init__(self, rpc: Client, local_pubkey: str):
        self.rpc = rpc
        self.local_pubkey = local_pubkey

    @staticmethod
    def get_last_index_offset() -> int:
        with session_scope() as session:
            record = (
                session
                .query(func.max(ForwardingEvents.last_index_offset))
                .scalar()
            )
            return record

    def upsert_all(self):
        forwarding_events = self.rpc.forwarding_history(
            start_time=1,
            end_time=int(datetime.now().timestamp()),
            num_max_events=10000,
            index_offset=self.get_last_index_offset()
        )
        log.debug(
            'forwarding_events',
            last_offset_index=forwarding_events.last_offset_index
        )
        csv_file = StringIO()
        writer = DictWriter(csv_file, fieldnames=ETLForwardingEvents.csv_columns)

        for forwarding_event in forwarding_events.forwarding_events:
            data = MessageToDict(forwarding_event)
            data['timestamp'] = datetime.utcfromtimestamp(
                forwarding_event.timestamp).replace(tzinfo=pytz.utc)
            data['channel_id_in'] = data.pop('chan_id_in')
            data['channel_id_out'] = data.pop('chan_id_out')
            data['amount_in'] = data.pop('amt_in')
            data['amount_out'] = data.pop('amt_out')
            data.pop('fee_msat')
            data.update(
                {'last_index_offset': forwarding_events.last_offset_index}
            )
            writer.writerow(data)

        ETLForwardingEvents.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLForwardingEvents,
                                    session.connection(),
                                    ETLForwardingEvents.csv_columns,
                                    **flags)
        ETLForwardingEvents.load()
        ETLForwardingEvents.truncate()
