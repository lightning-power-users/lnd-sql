import time

from grpc._channel import _Rendezvous

from lnd_grpc.lnd_grpc import Client
from lnd_grpc.protos.rpc_pb2 import GetInfoResponse
from lnd_sql.logger import log
from lnd_sql.scripts.upsert_channel_graph import UpsertChannelGraph
from lnd_sql.scripts.upsert_fiat_prices import cache_usd_price
from lnd_sql.scripts.upsert_forwarding_events import UpsertForwardingEvents
from lnd_sql.scripts.upsert_invoices import UpsertInvoices
from lnd_sql.scripts.upsert_open_channels import UpsertOpenChannels

import argparse

from lnd_sql.scripts.upsert_peers import UpsertPeers
from lnd_sql.scripts.upsert_pending_channels import UpsertPendingChannels
from lnd_sql.scripts.upsert_smart_fee_estimates import UpsertSmartFeeEstimates

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

    parser.add_argument(
        '--btc_conf_file',
        type=str,
        help='bitcoind config file',
    )

    args = parser.parse_args()

    rpc = Client(
        tls_cert_path=args.tls,
        grpc_host=args.host,
        grpc_port=args.port,
        macaroon_path=args.macaroon
    )

    info: GetInfoResponse = rpc.get_info()
    local_pubkey = info.identity_pubkey

    channel_graph = UpsertChannelGraph(rpc=rpc)
    forwarding_events = UpsertForwardingEvents(rpc=rpc, local_pubkey=local_pubkey)
    invoices = UpsertInvoices(rpc=rpc, local_pubkey=local_pubkey)
    open_channels = UpsertOpenChannels(rpc=rpc, local_pubkey=local_pubkey)
    peers = UpsertPeers(rpc=rpc, local_pubkey=local_pubkey)
    pending_channels = UpsertPendingChannels(rpc=rpc, local_pubkey=local_pubkey)
    smart_fee_estimates = UpsertSmartFeeEstimates(btc_conf_file=args.btc_conf_file)
    while True:
        try:
            log.debug('polling update starting')
            channel_graph.upsert_all()
            # forwarding_events.upsert_all()
            cache_usd_price()
            invoices.upsert_all()
            open_channels.upsert_all()
            peers.upsert_all()
            pending_channels.upsert_all()
            smart_fee_estimates.upsert_all()
            log.debug('polling update finished')
            time.sleep(30)
        except:
            log.error('polling error', exc_info=True)
            time.sleep(30)
