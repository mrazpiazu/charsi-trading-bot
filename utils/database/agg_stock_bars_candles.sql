WITH intervals AS (
  SELECT generate_series(
    TIMESTAMP :start_time,
    TIMESTAMP :end_time,
    INTERVAL :interval_string
  ) AS bucket_start
),
resampled AS (
  SELECT
    i.bucket_start as created_at,
    f.symbol AS symbol,
    FIRST_VALUE(f.open) OVER w AS open,
    LAST_VALUE(f.close) OVER w AS close,
    MAX(f.high) OVER w AS high,
    MIN(f.low) OVER w AS low,
    SUM(f.volume) OVER w AS volume,
    SUM(f.number_trades) OVER w AS number_trades
  FROM intervals i
  JOIN fact_stock_bars f
    ON f.created_at >= i.bucket_start
   AND f.created_at < i.bucket_start + INTERVAL :interval_string
  WINDOW w AS (
    PARTITION BY f.symbol, i.bucket_start
    ORDER BY f.created_at
    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
)
INSERT INTO agg_stock_bars (
  created_at, symbol, open, close, high, low, volume, number_trades
)
SELECT * FROM resampled;