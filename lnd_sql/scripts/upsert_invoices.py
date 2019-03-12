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
    _rpc: Client

    def __init__(self,
                 tls_cert_path: str = None,
                 macaroon_path: str = None,
                 lnd_grpc_host: str = '127.0.0.1',
                 lnd_grpc_port: str = '10009'):
        self._rpc = None
        self.tls_cert_path = tls_cert_path
        self.macaroon_path = macaroon_path
        self.lnd_grpc_host = lnd_grpc_host
        self.lnd_grpc_port = lnd_grpc_port

    @staticmethod
    def get_index_offset() -> int:
        with session_scope() as session:
            record = (
                session
                    .query(func.max(Invoices.last_index_offset)).scalar()
            )
            return record

    @property
    def rpc(self) -> Client:
        if self._rpc is None:
            self._rpc = Client(
                tls_cert_path=self.tls_cert_path,
                macaroon_path=self.macaroon_path,
                grpc_host=self.lnd_grpc_host,
                grpc_port=self.lnd_grpc_port,
            )
        return self._rpc

    def upsert_all(self):
        invoices: ListInvoiceResponse = self.rpc.list_invoices(
            num_max_invoices=100000,
            index_offset=self.get_index_offset()
        )
        info: GetInfoResponse = self.rpc.get_info()

        self.upsert(invoice_list=list(invoices.invoices),
                    last_index_offset=invoices.last_index_offset,
                    local_pubkey=info.identity_pubkey)

    @staticmethod
    def upsert(single_invoice=None, invoice_list=None,
               last_index_offset=None, local_pubkey=None):
        if invoice_list is None:
            invoice_list = [single_invoice]

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLInvoices.csv_columns)
        for invoice in invoice_list:
            invoice_dict = MessageToDict(invoice)
            invoice_dict['last_index_offset'] = last_index_offset
            invoice_dict['local_pubkey'] = local_pubkey
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
