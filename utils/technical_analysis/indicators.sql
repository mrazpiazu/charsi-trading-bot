WITH indicators AS (
  SELECT
    *,
    LAG(close) OVER (PARTITION BY symbol ORDER BY created_at) AS prev_close,
    LAG(high) OVER (PARTITION BY symbol ORDER BY created_at) AS prev_high,
    LAG(low) OVER (PARTITION BY symbol ORDER BY created_at) AS prev_low
  FROM agg_stock_bars
  WHERE
    created_at < :end_date
  ORDER BY created_at desc
  LIMIT 26
),
-- RSI (14)
rsi_step AS (
  SELECT *,
    GREATEST(close - prev_close, 0) AS gain,
    GREATEST(prev_close - close, 0) AS loss
  FROM indicators
),
rsi_avg AS (
  SELECT *,
    AVG(gain) OVER w AS avg_gain,
    AVG(loss) OVER w AS avg_loss
  FROM rsi_step
  WINDOW w AS (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW)
),
rsi_final AS (
  SELECT *,
    CASE
      WHEN avg_loss = 0 THEN 100
      ELSE 100 - (100 / (1 + avg_gain / avg_loss))
    END AS rsi
  FROM rsi_avg
),
-- EMA (12/26)
ema_calc AS (
  SELECT *,
    AVG(close) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) AS ema_12,
    AVG(close) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 25 PRECEDING AND CURRENT ROW) AS ema_26
  FROM rsi_final
),
-- MACD
macd_calc AS (
  SELECT *,
    ema_12 - ema_26 AS macd_line,
    AVG(ema_12 - ema_26) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 8 PRECEDING AND CURRENT ROW) AS macd_signal
  FROM ema_calc
),
-- SMA 20
sma_calc AS (
  SELECT *,
    AVG(close) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS sma_20
  FROM macd_calc
),
-- ATR 14
atr_step AS (
  SELECT *,
    GREATEST(high - low, ABS(high - prev_close), ABS(low - prev_close)) AS true_range
  FROM sma_calc
),
atr_final AS (
  SELECT *,
    AVG(true_range) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS atr_14
  FROM atr_step
),
-- ADX 14
adx_step AS (
  SELECT *,
    CASE WHEN (high - prev_high) > (prev_low - low) AND (high - prev_high) > 0 THEN high - prev_high ELSE 0 END AS plus_dm,
    CASE WHEN (prev_low - low) > (high - prev_high) AND (prev_low - low) > 0 THEN prev_low - low ELSE 0 END AS minus_dm
  FROM atr_final
),
adx_avg AS (
  SELECT *,
    AVG(plus_dm) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS plus_di,
    AVG(minus_dm) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS minus_di
  FROM adx_step
),
adx_final AS (
  SELECT *,
    100 * ABS(plus_di - minus_di) / NULLIF((plus_di + minus_di), 0) AS dx,
    AVG(100 * ABS(plus_di - minus_di) / NULLIF((plus_di + minus_di), 0)) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS adx_14
  FROM adx_avg
),
-- Stochastic Oscillator
stoch_calc AS (
  SELECT *,
    MAX(high) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS highest_high_14,
    MIN(low) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 13 PRECEDING AND CURRENT ROW) AS lowest_low_14
  FROM adx_final
),
stoch_final AS (
  SELECT *,
    100 * (close - lowest_low_14) / NULLIF((highest_high_14 - lowest_low_14), 0) AS stoch_k,
    AVG(100 * (close - lowest_low_14) / NULLIF((highest_high_14 - lowest_low_14), 0)) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS stoch_d
  FROM stoch_calc
),
-- Bollinger Bands
boll_calc AS (
  SELECT *,
    STDDEV(close) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS stddev_20,
    sma_20 + 2 * STDDEV(close) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS bb_upper,
    sma_20 - 2 * STDDEV(close) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS bb_lower
  FROM stoch_final
),
-- Pivot Points (Classic)
pivot_points AS (
  SELECT *,
    (prev_high + prev_low + prev_close) / 3 AS pivot,
    2 * ((prev_high + prev_low + prev_close) / 3) - prev_high AS support_1,
    2 * ((prev_high + prev_low + prev_close) / 3) - prev_low AS resistance_1
  FROM boll_calc
),
-- Donchian Channels (20)
donchian AS (
  SELECT *,
    MAX(high) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS donchian_upper,
    MIN(low) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS donchian_lower
  FROM pivot_points
),
-- CCI (20)
cci_calc AS (
  SELECT *,
    (high + low + close) / 3 AS typical_price
  FROM donchian
),
cci_final AS (
  SELECT *,
    AVG((high + low + close) / 3) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS cci_sma,
    STDDEV((high + low + close) / 3) OVER (PARTITION BY symbol ORDER BY created_at ROWS BETWEEN 19 PRECEDING AND CURRENT ROW) AS cci_stddev
  FROM cci_calc
),
cci_result AS (
  SELECT *,
    (typical_price - cci_sma) / (0.015 * NULLIF(cci_stddev, 0)) AS cci_20
  FROM cci_final
),
-- Rate of Change (ROC 12)
roc_calc AS (
  SELECT *,
    LAG(close, 12) OVER (PARTITION BY symbol ORDER BY created_at) AS close_12
  FROM cci_result
),
roc_final AS (
  SELECT *,
    100 * (close - close_12) / NULLIF(close_12, 0) AS roc_12
  FROM roc_calc
),
-- OBV
obv_calc AS (
  SELECT *,
    CASE
      WHEN close > prev_close THEN volume
      WHEN close < prev_close THEN -volume
      ELSE 0
    END AS obv_delta
  FROM roc_final
),
obv_final AS (
  SELECT *,
    SUM(obv_delta) OVER (PARTITION BY symbol ORDER BY created_at) AS obv
  FROM obv_calc
)
-- Final insert
INSERT INTO agg_bar_indicators (
  id,
  created_at,
  symbol,
  rsi,
  ema_12,
  ema_26,
  macd_line,
  macd_signal,
  sma_20,
  atr_14,
  adx_14,
  stochastic_oscillator_k,
  stochastic_oscillator_d,
  bollinger_bands_upper,
  bollinger_bands_lower,
  pivot,
  support_1,
  resistance_1,
  donchian_upper,
  donchian_lower,
  cci_20,
  roc_12,
  obv
)
SELECT
  id,
  created_at,
  symbol,
  rsi,
  ema_12,
  ema_26,
  macd_line,
  macd_signal,
  sma_20,
  atr_14,
  adx_14,
  stoch_k,
  stoch_d,
  bb_upper,
  bb_lower,
  pivot,
  support_1,
  resistance_1,
  donchian_upper,
  donchian_lower,
  cci_20,
  roc_12,
  obv
FROM obv_final;
