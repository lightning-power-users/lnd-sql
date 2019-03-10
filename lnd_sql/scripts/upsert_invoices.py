import csv
from datetime import datetime
from io import StringIO

# noinspection PyPackageRequirements
from google.protobuf.json_format import MessageToDict
import postgres_copy

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse, ListInvoiceResponse
from lnd_sql.database.session import session_scope
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

        invoices: ListInvoiceResponse = self.rpc.list_invoices()
        info: GetInfoResponse = self.rpc.get_info()

        csv_file = StringIO()
        writer = csv.DictWriter(csv_file,
                                fieldnames=ETLInvoices.csv_columns)
        for invoice in invoices.invoices:
            invoice_dict = MessageToDict(invoice)
            invoice_dict['local_pubkey'] = info.identity_pubkey
            invoice_dict['r_preimage'] = invoice.r_preimage.hex()
            invoice_dict['r_hash'] = invoice.r_hash.hex()
            invoice_dict['description_hash'] = invoice.description_hash.hex()
            invoice_dict['creation_date'] = datetime.utcfromtimestamp(invoice.creation_date)
            if invoice.settle_date:
                invoice_dict['settle_date'] = datetime.utcfromtimestamp(invoice.settle_date)
            else:
                invoice_dict['settle_date'] = None
            invoice_dict.pop('receipt', None)
            invoice_dict.pop('route_hints', None)
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
