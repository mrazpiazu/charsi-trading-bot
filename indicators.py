import pandas as pd


def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Relative Strength Index (RSI) for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'close' prices.
    period (int): The number of periods to use for RSI calculation.

    Returns:
    pd.Series: Series containing the RSI values.
    """
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


def calculate_sma(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Simple Moving Average (SMA) for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'close' prices.
    period (int): The number of periods to use for SMA calculation.

    Returns:
    pd.Series: Series containing the SMA values.
    """
    sma = df['close'].rolling(window=period).mean()
    return sma


def calculate_ema(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Exponential Moving Average (EMA) for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'close' prices.
    period (int): The number of periods to use for EMA calculation.

    Returns:
    pd.Series: Series containing the EMA values.
    """
    ema = df['close'].ewm(span=period, adjust=False).mean()
    return ema


def calculate_macd(df: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9) -> pd.DataFrame:
    """
    Calculate the Moving Average Convergence Divergence (MACD) for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'close' prices.
    short_window (int): The short window for MACD calculation.
    long_window (int): The long window for MACD calculation.
    signal_window (int): The signal line window for MACD calculation.

    Returns:
    pd.DataFrame: DataFrame containing the MACD and Signal values.
    """
    ema_short = df['close'].ewm(span=short_window, adjust=False).mean()
    ema_long = df['close'].ewm(span=long_window, adjust=False).mean()
    macd = ema_short - ema_long
    signal = macd.ewm(span=signal_window, adjust=False).mean()

    return pd.DataFrame({'MACD': macd, 'Signal': signal})


def calculate_bollinger_bands(df: pd.DataFrame, period: int = 20, num_std_dev: int = 2) -> pd.DataFrame:
    """
    Calculate the Bollinger Bands for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'close' prices.
    period (int): The number of periods to use for Bollinger Bands calculation.
    num_std_dev (int): The number of standard deviations to use for the bands.

    Returns:
    pd.DataFrame: DataFrame containing the upper and lower Bollinger Bands.
    """
    sma = df['close'].rolling(window=period).mean()
    std_dev = df['close'].rolling(window=period).std()

    upper_band = sma + (std_dev * num_std_dev)
    lower_band = sma - (std_dev * num_std_dev)

    return pd.DataFrame({'Upper Band': upper_band, 'lower Band': lower_band})


def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Average True Range (ATR) for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'high', 'low', and 'close' prices.
    period (int): The number of periods to use for ATR calculation.

    Returns:
    pd.Series: Series containing the ATR values.
    """
    high_low = df['high'] - df['low']
    high_prev_close = abs(df['high'] - df['close'].shift(1))
    low_prev_close = abs(df['low'] - df['close'].shift(1))

    tr = pd.concat([high_low, high_prev_close, low_prev_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()

    return atr


def calculate_stochastic_oscillator(df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
    """
    Calculate the Stochastic Oscillator for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'high', 'low', and 'close' prices.
    period (int): The number of periods to use for Stochastic Oscillator calculation.

    Returns:
    pd.DataFrame: DataFrame containing the %K and %D values.
    """
    low_min = df['low'].rolling(window=period).min()
    high_max = df['high'].rolling(window=period).max()

    k = 100 * ((df['close'] - low_min) / (high_max - low_min))
    d = k.rolling(window=3).mean()

    return pd.DataFrame({'%K': k, '%D': d})


def calculate_adx(df: pd.DataFrame, period: int = 14) -> pd.Series:
    """
    Calculate the Average Directional Index (ADX) for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'high', 'low', and 'close' prices.
    period (int): The number of periods to use for ADX calculation.

    Returns:
    pd.Series: Series containing the ADX values.
    """
    high = df['high']
    low = df['low']
    close = df['close']

    tr = calculate_atr(df, period)
    plus_dm = high.diff().where((high.diff() > low.diff()) & (high.diff() > 0), 0)
    minus_dm = low.diff().where((low.diff() > high.diff()) & (low.diff() > 0), 0)

    plus_di = 100 * (plus_dm.rolling(window=period).mean() / tr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / tr)

    adx = 100 * ((plus_di - minus_di).abs() / (plus_di + minus_di)).rolling(window=period).mean()

    return adx


def calculate_ichimoku(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate the Ichimoku Cloud indicators for a given DataFrame.

    Parameters:
    df (pd.DataFrame): DataFrame containing 'high', 'low', and 'close' prices.

    Returns:
    pd.DataFrame: DataFrame containing the Ichimoku Cloud indicators.
    """
    high = df['high']
    low = df['low']
    close = df['close']

    nine_period_high = high.rolling(window=9).max()
    nine_period_low = low.rolling(window=9).min()
    senkou_span_a = ((nine_period_high + nine_period_low) / 2).shift(26)

    senkou_span_b = ((high.rolling(window=52).max() + low.rolling(window=52).min()) / 2).shift(26)
    tenkan_sen = ((high.rolling(window=9).max() + low.rolling(window=9).min()) / 2)
    kijun_sen = ((high.rolling(window=26).max() + low.rolling(window=26).min()) / 2)

    return pd.DataFrame({
        'Senkou Span A': senkou_span_a,
        'Senkou Span B': senkou_span_b,
        'Tenkan-sen': tenkan_sen,
        'Kijun-sen': kijun_sen
    })