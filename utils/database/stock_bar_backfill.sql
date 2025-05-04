WITH params AS (
  SELECT
    TIMESTAMP :start_time AS start_time,
    TIMESTAMP :end_time AS end_time
),
symbols AS (
  SELECT DISTINCT symbol FROM stock_bars
),
minutes AS (
  SELECT
    s.symbol,
    generate_series(p.start_time, p.end_time - INTERVAL '1 minute', INTERVAL '1 minute') AS created_at
  FROM symbols s, params p
),
historical_data AS (
  SELECT
    symbol,
    created_at,
    open,
    close,
    high,
    low,
    volume,
    number_trades,
    volume_weighted_average_price,
    FALSE AS is_imputed
  FROM stock_bars
  WHERE created_at < (SELECT end_time FROM params)
),
only_missing_minutes AS (
  SELECT m.*
  FROM minutes m
  LEFT JOIN stock_bars h
    ON h.symbol = m.symbol AND h.created_at = m.created_at
  WHERE h.created_at IS NULL
),
unioned AS (
  SELECT * FROM historical_data
  UNION ALL
  SELECT
    symbol,
    created_at,
    NULL::NUMERIC, NULL::NUMERIC, NULL::NUMERIC, NULL::NUMERIC,
    0::NUMERIC, 0::INTEGER, NULL::NUMERIC,
    TRUE AS is_imputed
  FROM only_missing_minutes
),
filled AS (
  SELECT
    symbol,
    created_at,
    MAX(open) OVER w AS open,
    MAX(close) OVER w AS close,
    MAX(high) OVER w AS high,
    MAX(low) OVER w AS low,
    CASE
      WHEN volume = 0 AND is_imputed THEN 0
      ELSE MAX(volume) OVER w
    END AS volume,
    CASE
      WHEN number_trades = 0 AND is_imputed THEN 0
      ELSE MAX(number_trades) OVER w
    END AS number_trades,
    MAX(volume_weighted_average_price) OVER w AS volume_weighted_average_price,
    is_imputed
  FROM unioned
  WINDOW w AS (
    PARTITION BY symbol ORDER BY created_at
    ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
  )
),
final AS (
  SELECT *
  FROM filled
  WHERE created_at >= (SELECT start_time FROM params)
    AND is_imputed = TRUE
)
INSERT INTO stock_bars (
  symbol,
  created_at,
  open,
  close,
  high,
  low,
  volume,
  number_trades,
  volume_weighted_average_price,
  is_imputed
)
SELECT
  symbol,
  created_at,
  open,
  close,
  high,
  low,
  volume,
  number_trades,
  volume_weighted_average_price,
  is_imputed
FROM final;
