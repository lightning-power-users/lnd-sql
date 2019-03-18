import argparse
from datetime import datetime, timedelta

import pytz
from google.protobuf.json_format import MessageToDict
from sqlalchemy import and_

from bitcoin.rpc import Proxy
from lnd_grpc.lnd_grpc import Client
from lnd_sql import session_scope
from lnd_sql.logger import log
from lnd_sql.models import OpenChannels, InboundCapacityRequest


def close_channels(rpc: Client, btc_conf_file: str):
    with session_scope() as session:
        channels = (
            session.query(OpenChannels)
                .filter(
                and_(
                    OpenChannels.total_satoshis_sent.is_(None),
                    OpenChannels.total_satoshis_received.is_(None),
                    OpenChannels.local_balance.isnot(None),
                    OpenChannels.remote_balance.is_(None)
                )
            ).all()
        )
        for channel in channels:
            txid = channel.channel_point.split(':')[0]
            # noinspection PyProtectedMember
            tx = Proxy(btc_conf_file=btc_conf_file)._call('getrawtransaction', txid, True)
            blocktime = datetime.utcfromtimestamp(tx['blocktime']).replace(tzinfo=pytz.utc)
            inbound_capacity_requests = (
                session.query(InboundCapacityRequest)
                .filter(InboundCapacityRequest.remote_pubkey == channel.remote_pubkey)
                .all()
            )
            if inbound_capacity_requests:
                continue
            one_week_ago = datetime.utcnow().replace(tzinfo=pytz.utc) - timedelta(weeks=1)
            if blocktime > one_week_ago:
                continue

            force = not channel.active
            channel_close_updates = rpc.close_channel(
                channel_point=channel.channel_point,
                force=force,
                sat_per_byte=1
            )
            for channel_close_update in channel_close_updates:
                log.info('channel_close_update',
                         channel_close_update=MessageToDict(channel_close_update)
                         )
                break


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

    close_channels(rpc, args.btc_conf_file)
