SELECT
      percentile_disc(0.96) within group (order by fee_rate_milli_msat),
      percentile_disc(0.95) within group (order by fee_rate_milli_msat),
      percentile_disc(0.94) within group (order by fee_rate_milli_msat),
      percentile_disc(0.93) within group (order by fee_rate_milli_msat),
      percentile_disc(0.9) within group (order by fee_rate_milli_msat),
      percentile_disc(0.8) within group (order by fee_rate_milli_msat),
      percentile_disc(0.5) within group (order by fee_rate_milli_msat),
      percentile_disc(0.1) within group (order by fee_rate_milli_msat)
FROM routing_policies;