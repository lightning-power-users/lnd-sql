import time

from lnd_sql.scripts.upsert_forwarding_events import UpsertForwardingEvents
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

    fwd_events = UpsertForwardingEvents(
        tls_cert_path=args.tls,
        lnd_grpc_host=args.host,
        lnd_grpc_port=args.port,
        macaroon_path=args.macaroon
    )

    while True:
        UpsertOpenChannels(
            tls_cert_path=args.tls,
            lnd_grpc_host=args.host,
            lnd_grpc_port=args.port,
            macaroon_path=args.macaroon
        )
        fwd_events.upsert_all()
        time.sleep(60)
