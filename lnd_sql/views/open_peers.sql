SELECT ln.alias,
       open_peers.*,
       open_peers.our_capacity - open_peers.local_balance - open_peers.remote_balance - open_peers.commit_fee - open_peers.unsettled_balance AS capacity_rec,
       open_peers_channels.total_channel_count,
       open_peers_channels.total_channel_capacity,
       round(open_peers.our_capacity / open_peers_channels.total_channel_capacity*100) as percent_ours
  FROM
(SELECT
       remote_pubkey,
       count(chan_id) AS our_chan_count,
       sum(capacity) AS our_capacity,
       coalesce(sum(local_balance), 0) AS local_balance,
       coalesce(sum(remote_balance), 0) AS remote_balance,
       coalesce(sum(commit_fee), 0) AS commit_fee,
       coalesce(sum(unsettled_balance), 0) AS unsettled_balance
FROM open_channels
GROUP BY remote_pubkey) open_peers
LEFT JOIN
(
  SELECT
         pubkey,
         sum(total_channel_count) AS total_channel_count,
         sum(total_channel_capacity) AS total_channel_capacity
  FROM
  (SELECT
         channel_edges.node1_pubkey AS pubkey,
         count(channel_edges.id) AS total_channel_count,
          sum(channel_edges.capacity) as total_channel_capacity
  FROM channel_edges
  GROUP BY channel_edges.node1_pubkey
  UNION
  SELECT
        channel_edges.node2_pubkey AS pubkey,
         count(channel_edges.id) AS total_channel_count,
        sum(channel_edges.capacity) as total_channel_capacity
  FROM channel_edges
  GROUP BY channel_edges.node2_pubkey) peer_channel_counts
  GROUP BY pubkey
  ORDER BY sum(total_channel_count) desc
) open_peers_channels ON open_peers_channels.pubkey = open_peers.remote_pubkey
LEFT OUTER JOIN lightning_nodes ln
ON ln.pubkey = open_peers.remote_pubkey

LEFT JOIN
(
  SELECT pubkey
  SELECT * FROM (
                SELECT channel_id_
                  ) t2
  ) t
ON t.pubkey = open_peers.remote_pubkey
ORDER BY open_peers.our_chan_count DESC, open_peers.our_capacity DESC, open_peers_channels.total_channel_capacity DESC;