WITH minute_series AS (
  SELECT generate_series(
    :start_time::timestamp,
    :end_time::timestamp,
    interval '1 minute'
  ) AS created_at
),
all_minutes AS (
  SELECT :symbol AS symbol, ms.created_at
  FROM minute_series ms
),
latest_values AS (
  SELECT
    am.symbol,
    am.created_at,
    sb.open,
    sb.close,
    sb.high,
    sb.low,
    sb.volume,
    sb.number_trades,
    sb.volume_weighted_average_price
  FROM all_minutes am
  LEFT JOIN LATERAL (
    SELECT open, close, high, low, volume, number_trades, volume_weighted_average_price
    FROM stock_bars sb
    WHERE sb.symbol = am.symbol
      AND sb.created_at <= am.created_at
    ORDER BY sb.created_at DESC
    LIMIT 1
  ) sb ON TRUE
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
  volume_weighted_average_price
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
  volume_weighted_average_price
FROM latest_values
WHERE open IS NOT NULL
ORDER BY created_at;
