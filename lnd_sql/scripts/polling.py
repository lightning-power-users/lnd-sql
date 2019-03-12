import time

from grpc._channel import _Rendezvous

from lnd_sql.logger import log
from lnd_sql.scripts.upsert_forwarding_events import UpsertForwardingEvents
from lnd_sql.scripts.upsert_invoices import UpsertInvoices
from lnd_sql.scripts.upsert_open_channels import UpsertOpenChannels

import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Polling to keep the SQL data fresh'
    )

    parser.add_argument(
        '--macaroon',
        '-m',
        type=str
    )

    parser.add_argument(
        '--tls',
        '-t',
        type=str
    )

    parser.add_argument(
        '--port',
        type=str,
        help='Port for gRPC',
        default='10009'
    )

    parser.add_argument(
        '--host',
        type=str,
        help='Host IP address for gRPC',
        default='127.0.0.1'
    )

    args = parser.parse_args()
    invoices = UpsertInvoices(
        tls_cert_path=args.tls,
        lnd_grpc_host=args.host,
        lnd_grpc_port=args.port,
        macaroon_path=args.macaroon
    )
    while True:
        try:
            # UpsertOpenChannels(
            #     tls_cert_path=args.tls,
            #     lnd_grpc_host=args.host,
            #     lnd_grpc_port=args.port,
            #     macaroon_path=args.macaroon
            # )
            # log.debug('polling update')

            invoices.upsert_all()
            log.debug('polling update')

            # fwd_events = UpsertForwardingEvents(
            #     tls_cert_path=args.tls,
            #     lnd_grpc_host=args.host,
            #     lnd_grpc_port=args.port,
            #     macaroon_path=args.macaroon
            # )
        except _Rendezvous:
            log.error('polling error', exc_info=True)
            time.sleep(1)
