SELECT open_channels.remote_pubkey,
       their_node.alias,
       open_channels.chan_id,
       open_channels.capacity,
       our_routing_policies.fee_base_msat AS our_base_fee,
       our_routing_policies.fee_rate_milli_msat AS our_fee_rate,
       count(out_forwarding_events.id)       out_10_day_count_pmts,
       sum(out_forwarding_events.amount_out) out_10_day_total_pmts,
       count(in_forwarding_events.id)        in_10_day_count_pmts,
       sum(in_forwarding_events.amount_in)   in_10_day_total_pmts,
       sum(in_forwarding_events.fee)         fee_10_day_total
from open_channels
       JOIN forwarding_events out_forwarding_events
            ON out_forwarding_events.channel_id_out = open_channels.chan_id
              and out_forwarding_events.timestamp >
                  current_date - interval '10' day
       JOIN forwarding_events in_forwarding_events
            ON in_forwarding_events.channel_id_in = open_channels.chan_id
              and
               in_forwarding_events.timestamp > current_date - interval '10' day

       JOIN routing_policies our_routing_policies
            ON our_routing_policies.channel_id = open_channels.chan_id
              AND our_routing_policies.pubkey = open_channels.local_pubkey
       JOIN lightning_nodes their_node
              ON their_node.pubkey = open_channels.remote_pubkey
GROUP BY open_channels.remote_pubkey, open_channels.chan_id,
         open_channels.capacity, our_routing_policies.fee_base_msat,
         our_routing_policies.fee_base_msat, fee_rate_milli_msat,
         their_node.alias
HAVING count(in_forwarding_events.id) > 10
AND sum(in_forwarding_events.amount_in) > 100000
ORDER BY in_10_day_total_pmts DESC, capacity DESC, remote_pubkey;
