from datetime import datetime
import pandas as pd
from sqlalchemy import text
from utils.database.db import SessionLocal
from utils.logger.logger import get_logger_config
import logging

logger = logging.getLogger("indicators_pandas")
get_logger_config(logging)

# --- CONFIG ---
AGG_TABLE = "agg_stock_bars"
INDICATOR_TABLE = "agg_bar_indicators"

# --- INDICATOR FUNCTIONS ---

def add_previous_columns(df):
    df["prev_close"] = df["close"].shift(1)
    df["prev_high"] = df["high"].shift(1)
    df["prev_low"] = df["low"].shift(1)
    return df

import numpy as np
import pandas as pd


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.set_index("created_at", inplace=True)
    df.sort_index(inplace=True)

    # Previo
    df["prev_close"] = df["close"].shift(1)
    df["prev_high"] = df["high"].shift(1)
    df["prev_low"] = df["low"].shift(1)

    # RSI (14) con EMA (Wilder)
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1/14, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1/14, adjust=False).mean()
    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # EMA 12 y 26
    df["ema_12"] = df["close"].ewm(span=12, adjust=False).mean()
    df["ema_26"] = df["close"].ewm(span=26, adjust=False).mean()

    # MACD
    df["macd_line"] = df["ema_12"] - df["ema_26"]
    df["macd_signal"] = df["macd_line"].ewm(span=9, adjust=False).mean()

    # SMA 20
    df["sma_20"] = df["close"].rolling(window=20).mean()

    # ATR (14)
    tr1 = df["high"] - df["low"]
    tr2 = abs(df["high"] - df["prev_close"])
    tr3 = abs(df["low"] - df["prev_close"])
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    df["atr_14"] = tr.rolling(window=14).mean()

    # ADX (14)
    df["up_move"] = df["high"] - df["high"].shift(1)
    df["down_move"] = df["low"].shift(1) - df["low"]
    df["plus_dm"] = np.where((df["up_move"] > df["down_move"]) & (df["up_move"] > 0), df["up_move"], 0)
    df["minus_dm"] = np.where((df["down_move"] > df["up_move"]) & (df["down_move"] > 0), df["down_move"], 0)
    df["tr"] = pd.concat([
        df["high"] - df["low"],
        abs(df["high"] - df["close"].shift(1)),
        abs(df["low"] - df["close"].shift(1))
    ], axis=1).max(axis=1)
    atr_14 = df["tr"].rolling(window=14).mean()
    plus_di_14 = 100 * df["plus_dm"].rolling(window=14).sum() / atr_14
    minus_di_14 = 100 * df["minus_dm"].rolling(window=14).sum() / atr_14
    dx = (abs(plus_di_14 - minus_di_14) / (plus_di_14 + minus_di_14)) * 100
    df["adx_14"] = dx.rolling(window=14).mean()

    # Stochastic Oscillator
    low_14 = df["low"].rolling(window=14).min()
    high_14 = df["high"].rolling(window=14).max()
    df["stochastic_oscillator_k"] = 100 * (df["close"] - low_14) / (high_14 - low_14)
    df["stochastic_oscillator_d"] = df["stochastic_oscillator_k"].rolling(window=3).mean()

    # Bollinger Bands
    std_20 = df["close"].rolling(window=20).std()
    df["bollinger_bands_upper"] = df["sma_20"] + 2 * std_20
    df["bollinger_bands_lower"] = df["sma_20"] - 2 * std_20

    # Pivot Points (Classic)
    pivot = (df["prev_high"] + df["prev_low"] + df["prev_close"]) / 3
    df["pivot"] = pivot
    df["support_1"] = 2 * pivot - df["prev_high"]
    df["resistance_1"] = 2 * pivot - df["prev_low"]

    # Donchian Channels (20)
    df["donchian_upper"] = df["high"].rolling(window=20).max()
    df["donchian_lower"] = df["low"].rolling(window=20).min()

    # CCI (20)
    tp = (df["high"] + df["low"] + df["close"]) / 3
    cci_sma = tp.rolling(window=20).mean()
    cci_std = tp.rolling(window=20).std()
    df["cci_20"] = (tp - cci_sma) / (0.015 * cci_std)

    # ROC (12)
    df["roc_12"] = 100 * (df["close"] - df["close"].shift(12)) / df["close"].shift(12)

    # OBV
    obv = [0]
    for i in range(1, len(df)):
        if df["close"].iloc[i] > df["close"].iloc[i-1]:
            obv.append(obv[-1] + df["volume"].iloc[i])
        elif df["close"].iloc[i] < df["close"].iloc[i-1]:
            obv.append(obv[-1] - df["volume"].iloc[i])
        else:
            obv.append(obv[-1])
    df["obv"] = obv

    df.reset_index(inplace=True)
    return df


# --- DB FUNCTIONS ---

def fetch_ohlcv(session, symbol, start_date, end_date, aggregation):
    query = text(f"""
        SELECT created_at, symbol, open, close, high, low, volume, number_trades, volume_weighted_average_price
        FROM {AGG_TABLE}
        WHERE 
            symbol = :symbol AND 
            created_at BETWEEN :start AND :end AND
            aggregation = :aggregation
        ORDER BY created_at
    """)
    result = session.execute(query, {"symbol": symbol, "start": start_date, "end": end_date, "aggregation": aggregation})
    return pd.DataFrame(result.fetchall(), columns=result.keys())

def delete_existing_indicators(session, symbol, start_date, end_date):
    delete_query = text(f"""
        DELETE FROM {INDICATOR_TABLE}
        WHERE symbol = :symbol
        AND created_at BETWEEN :start AND :end
    """)
    session.execute(delete_query, {"symbol": symbol, "start": start_date, "end": end_date})
    session.commit()


def insert_indicators(session, df):
    cols = [
        "created_at", "symbol", "rsi", "ema_12", "ema_26", "macd_line", "macd_signal",
        "sma_20", "atr_14", "adx_14", "stochastic_oscillator_k", "stochastic_oscillator_d",
        "bollinger_bands_upper", "bollinger_bands_lower", "pivot", "support_1", "resistance_1",
        "donchian_upper", "donchian_lower", "cci_20", "roc_12", "obv"
    ]
    df = df[cols].dropna(subset=["rsi"])
    df.to_sql(INDICATOR_TABLE, session.bind, if_exists="append", index=False)


def get_unique_symbols(session, start_date, end_date):
    query = text(f"""
        WITH counted_bars AS (
            SELECT
                symbol,
                COUNT(*) AS actual_count
            FROM {AGG_TABLE}
            WHERE created_at >= :start_date
                AND created_at < :end_date
            GROUP BY symbol
            HAVING COUNT(*) >= 100
        )
        SELECT 
            cb.symbol
        FROM counted_bars cb
    """)
    result = session.execute(query, {"start_date": start_date, "end_date": end_date})
    return [row[0] for row in result.fetchall()]


# --- MAIN EXECUTION ---

def main(start_date: datetime, end_date: datetime, aggregation):

    start_date = start_date - timedelta(days=7)

    session = SessionLocal()

    symbols = get_unique_symbols(session, start_date, end_date)

    try:
        for symbol in symbols:
            print(f"[INFO] Processing {symbol}")
            df = fetch_ohlcv(session, symbol, start_date, end_date, aggregation)
            if df.empty:
                print(f"[WARN] No data for {symbol}, skipping.")
                continue
            enriched = calculate_indicators(df)
            delete_existing_indicators(session, symbol, start_date, end_date)
            insert_indicators(session, enriched)
            print(f"[OK] Inserted indicators for {symbol}")
    except Exception as e:
        logger.error(f"Error processing indicators: {e}")
        session.rollback()
    finally:
        session.close()


if __name__ == "__main__":
    from datetime import timedelta

    start_date = datetime(2025, 5, 8, 16, 0, 0)
    end_date = start_date + timedelta(minutes=15)
    aggregation = "15 minutes"

    main(start_date, end_date, aggregation)