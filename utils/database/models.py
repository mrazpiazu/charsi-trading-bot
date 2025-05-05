from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone

Base = declarative_base()


class Stock(Base):
    __tablename__ = 'dim_stocks'
    id = Column(Integer, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    symbol = Column(String(10), primary_key=True)


class StockBar(Base):
    __tablename__ = 'fact_stock_bars'
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
    is_imputed = Boolean()


class StockBarAggregate(Base):
    __tablename__ = 'agg_stock_bars'
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
    aggregation = Column(String(10))  # e.g., "1D", "1H", "15m"


class StockIndicator(Base):
    __tablename__ = 'agg_bar_indicators'

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


class StockOrder(Base):
    __tablename__ = 'fact_stock_orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    submitted_at = Column(DateTime)
    filled_at = Column(DateTime)
    canceled_at = Column(DateTime)

    symbol = Column(String(10))
    order_id = Column(String(50))  # Alpaca order ID
    client_order_id = Column(String(50), nullable=True)

    side = Column(String(10))  # "buy" or "sell"
    type = Column(String(20))  # "market", "limit", "stop", "stop_limit", etc.
    order_type = Column(String(20))  # can drop if redundant with `type`
    status = Column(String(20))  # "new", "filled", "canceled", etc.

    quantity = Column(Integer)
    filled_quantity = Column(Integer)
    price = Column(Float)  # intended price
    limit_price = Column(Float, nullable=True)
    stop_price = Column(Float, nullable=True)
    trail_price = Column(Float, nullable=True)
    trail_percent = Column(Float, nullable=True)

    time_in_force = Column(String(10))  # "gtc", "day", etc.
    extended_hours = Column(Boolean, default=False)

    parent_order_id = Column(String(50), nullable=True)
    take_profit_price = Column(Float, nullable=True)
    stop_loss_price = Column(Float, nullable=True)

    is_simulated = Column(Boolean, default=False)


class StockTrade(Base):
    __tablename__ = 'fact_stock_trades'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    filled_at = Column(DateTime)

    symbol = Column(String(10))
    trade_id = Column(String(50), unique=True)
    order_id = Column(String(50))  # foreign key to StockOrder if needed

    quantity = Column(Integer)
    price = Column(Float)
    commission = Column(Float, default=0.0)
    profit_loss = Column(Float)
    is_simulated = Column(Boolean, default=False)
