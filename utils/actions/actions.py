import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

# -----------------------------------------
# Evaluate technical signals
# -----------------------------------------
def evaluate_signals(candles, median_close):
    current_close = candles.iloc[-1]['close']
    rsi = candles.iloc[-1]['rsi']
    macd = candles.iloc[-1]['macd']
    bb_pos = candles.iloc[-1]['bollinger_band_position']

    signals = []

    if current_close < median_close * 0.99:
        signals.append("price below median (buy)")
    elif current_close > median_close * 1.01:
        signals.append("price above median (sell)")

    if rsi < 30:
        signals.append("RSI oversold (buy)")
    elif rsi > 70:
        signals.append("RSI overbought (sell)")

    if macd > 0:
        signals.append("MACD positive (bullish)")
    elif macd < 0:
        signals.append("MACD negative (bearish)")

    if bb_pos < 0.25:
        signals.append("near lower Bollinger Band (buy)")
    elif bb_pos > 0.75:
        signals.append("near upper Bollinger Band (sell)")

    score = sum(
        1 if "buy" in s else -1 if "sell" in s else 0 for s in signals
    )

    if score >= 2:
        decision = 'buy'
    elif score <= -2:
        decision = 'sell'
    else:
        decision = 'hold'

    return decision, signals

# -----------------------------------------
# Calculate entry strategy, SL/TP and estimated time
# -----------------------------------------
def calculate_strategy(candles, decision, stop_loss_pct, take_profit_pct, recent_candle_count):
    if decision not in ['buy', 'sell']:
        return None, None, None, None

    if decision == 'buy':
        optimal_price = candles['low'][-recent_candle_count:].mean()
        stop_loss = optimal_price * (1 - stop_loss_pct)
        take_profit = optimal_price * (1 + take_profit_pct)
    else:
        optimal_price = candles['high'][-recent_candle_count:].mean()
        stop_loss = optimal_price * (1 + stop_loss_pct)
        take_profit = optimal_price * (1 - take_profit_pct)

    avg_range = (candles['high'] - candles['low'])[-recent_candle_count:].mean()
    if avg_range == 0:
        estimated_time_min = 15
    else:
        estimated_candles = abs(take_profit - optimal_price) / avg_range
        estimated_time_min = max(1, int(estimated_candles)) * 15

    return round(optimal_price, 2), round(stop_loss, 2), round(take_profit, 2), estimated_time_min

# -----------------------------------------
# Process a single symbol
# -----------------------------------------
def process_symbol(symbol, group_df, config):
    if len(group_df) < config['observation_window']:
        return {
            'symbol': symbol,
            'decision': 'hold',
            'reason': 'Not enough candles',
            'optimal_price': None,
            'stop_loss': None,
            'take_profit': None,
            'estimated_time_min': None
        }

    candles = group_df.tail(config['observation_window']).copy()
    median_close = np.percentile(candles['close'][:-1], 50)
    decision, signals = evaluate_signals(candles, median_close)

    optimal_price, stop_loss, take_profit, estimated_time = calculate_strategy(
        candles, decision,
        config['stop_loss_pct'],
        config['take_profit_pct'],
        config['recent_candle_count']
    )

    return {
        'symbol': symbol,
        'decision': decision,
        'reason': "; ".join(signals),
        'optimal_price': optimal_price,
        'stop_loss': stop_loss,
        'take_profit': take_profit,
        'estimated_time_min': estimated_time
    }

# -----------------------------------------
# Evaluate all symbols in parallel
# -----------------------------------------
def evaluate_all_symbols(candle_df, config=None):
    if config is None:
        config = {
            'observation_window': 30,
            'recent_candle_count': 10,
            'stop_loss_pct': 0.02,
            'take_profit_pct': 0.04
        }

    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = []
        for symbol, group in candle_df.groupby('symbol'):
            futures.append(executor.submit(process_symbol, symbol, group, config))

        for f in futures:
            results.append(f.result())

    return pd.DataFrame(results)

# -----------------------------------------
# Example usage
# -----------------------------------------
if __name__ == "__main__":
    np.random.seed(42)
    symbols = ['AAPL', 'TSLA', 'GOOG']
    rows = []
    for symbol in symbols:
        for _ in range(30):
            rows.append({
                'symbol': symbol,
                'close': np.random.uniform(100, 110),
                'rsi': np.random.uniform(20, 80),
                'macd': np.random.uniform(-2, 2),
                'bollinger_band_position': np.random.uniform(0, 1)
            })

    candles_df = pd.DataFrame(rows)
    results_df = evaluate_all_symbols(candles_df)
    print(results_df)
