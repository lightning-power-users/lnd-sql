import csv
from datetime import datetime
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy
import pytz
from sqlalchemy import func

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse, ListInvoiceResponse
from lnd_sql.database.session import session_scope
from lnd_sql.models import Invoices
from lnd_sql.models.lnd.etl.etl_invoices import ETLInvoices


class UpsertInvoices(object):
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

        self.info: GetInfoResponse = self.rpc.get_info()

    @staticmethod
    def get_index_offset() -> int:
        with session_scope() as session:
            record = (
                session
                    .query(func.max(Invoices.last_index_offset)).scalar()
            )
            return record

    def upsert_all(self):
        invoices: ListInvoiceResponse = self.rpc.list_invoices(
            num_max_invoices=100000,
            index_offset=self.get_index_offset()
        )
        self.upsert(invoice_list=invoices.invoices,
                    last_index_offset=invoices.last_index_offset)

    def upsert(self, invoice_list, last_index_offset=None):
        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLInvoices.csv_columns)
        for invoice in invoice_list:
            invoice_dict = MessageToDict(invoice)
            invoice_dict['last_index_offset'] = last_index_offset
            invoice_dict['local_pubkey'] = self.info.identity_pubkey
            invoice_dict['r_preimage'] = invoice.r_preimage.hex()
            invoice_dict['r_hash'] = invoice.r_hash.hex()
            invoice_dict['description_hash'] = invoice.description_hash.hex()
            invoice_dict['creation_date'] = datetime.utcfromtimestamp(
                invoice.creation_date).replace(tzinfo=pytz.utc)
            if invoice.settle_date:
                invoice_dict['settle_date'] = datetime.utcfromtimestamp(
                    invoice.settle_date).replace(tzinfo=pytz.utc)
            else:
                invoice_dict['settle_date'] = None
            invoice_dict.pop('receipt', None)
            invoice_dict.pop('route_hints', None)
            invoice_dict.pop('amt_paid', None)
            invoice_dict.pop('amt_paid_msat', None)
            writer.writerow(invoice_dict)
        ETLInvoices.truncate()
        flags = {'format': 'csv', 'header': False}
        with session_scope() as session:
            csv_file.seek(0)
            postgres_copy.copy_from(csv_file,
                                    ETLInvoices,
                                    session.connection(),
                                    ETLInvoices.csv_columns,
                                    **flags)
        ETLInvoices.load()
        ETLInvoices.truncate()
