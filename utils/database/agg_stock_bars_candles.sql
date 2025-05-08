WITH intervals AS (
  SELECT generate_series(
    TIMESTAMP :start_time,
    TIMESTAMP :end_time,
    INTERVAL :aggregation
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
    SUM(f.number_trades) OVER w AS number_trades,
    SUM(f.volume * f.close) OVER w / NULLIF(SUM(f.volume) OVER w, 0) AS volume_weighted_average_price,
    :aggregation AS aggregation
  FROM intervals i
  JOIN fact_stock_bars f
    ON f.created_at >= i.bucket_start
   AND f.created_at < i.bucket_start + INTERVAL :aggregation
  WINDOW w AS (
    PARTITION BY f.symbol, i.bucket_start
    ORDER BY f.created_at
    RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
  )
)
INSERT INTO agg_stock_bars (
  created_at, symbol, open, close, high, low, volume, number_trades, volume_weighted_average_price, aggregation
)
SELECT * FROM resampled;