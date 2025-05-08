WITH intervals AS (
  SELECT generate_series(
    TIMESTAMP :start_time,
    TIMESTAMP :end_time,
    INTERVAL :aggregation
  ) AS bucket_start
),
joined AS (
  SELECT
    i.bucket_start,
    f.symbol,
    f.created_at,
    f.open,
    f.close,
    f.high,
    f.low,
    f.volume,
    f.number_trades
  FROM intervals i
  JOIN fact_stock_bars f
    ON f.created_at >= i.bucket_start
   AND f.created_at < i.bucket_start + INTERVAL :aggregation
),
resampled AS (
  SELECT
    bucket_start AS created_at,
    symbol,
    FIRST_VALUE(open) OVER w AS open,
    LAST_VALUE(close) OVER w AS close,
    MAX(high) AS high,
    MIN(low) AS low,
    SUM(volume) AS volume,
    SUM(number_trades) AS number_trades,
    SUM(volume * close)::NUMERIC / NULLIF(SUM(volume), 0) AS volume_weighted_average_price,
    :aggregation AS aggregation
  FROM joined
  WINDOW w AS (
    PARTITION BY symbol, bucket_start ORDER BY created_at
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
  GROUP BY bucket_start, symbol
)
