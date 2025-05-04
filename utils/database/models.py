from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()


class Stock(Base):
    __tablename__ = 'stocks'
    id = Column(Integer, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    symbol = Column(String(10), primary_key=True)


class StockBar(Base):
    __tablename__ = 'stock_bars'
    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    symbol = Column(String(10))
    open = Column(Float)
    close = Column(Float)
    high = Column(Float)
    low = Column(Float)
    volume = Column(Float)
    number_trades = Column(Integer)
    volume_weighted_average_price = Column(Float)
    is_imputed = Boolean(default=False)


class StockIndicator(Base):
    __tablename__ = 'bar_indicators'

    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    symbol = Column(String(10))

    # Core Indicators
    rsi = Column(Float)
    ema_12 = Column(Float)
    ema_26 = Column(Float)
    macd_line = Column(Float)
    macd_signal = Column(Float)
    sma_20 = Column(Float)
    atr_14 = Column(Float)
    atr = Column(Float)  # Optional/legacy
    adx_14 = Column(Float)

    # Oscillators
    stochastic_oscillator_k = Column(Float)
    stochastic_oscillator_d = Column(Float)

    # Bollinger Bands
    bollinger_bands_upper = Column(Float)
    bollinger_bands_lower = Column(Float)

    # Pivot Points
    pivot = Column(Float)
    support_1 = Column(Float)
    resistance_1 = Column(Float)

    # Donchian Channels
    donchian_upper = Column(Float)
    donchian_lower = Column(Float)

    # Commodity Channel Index
    cci_20 = Column(Float)

    # Rate of Change
    roc_12 = Column(Float)

    # On-Balance Volume
    obv = Column(Float)