from sqlalchemy import create_engine, Column, Integer, String, DateTime
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
    open = Column(Integer)
    close = Column(Integer)
    high = Column(Integer)
    low = Column(Integer)
    volume = Column(Integer)
    number_trades = Column(Integer)
    volume_weighted_average_price = Column(Integer)


class StockIndicator(Base):
    __tablename__ = 'bar_indicators'
    id = Column(Integer, autoincrement=True, primary_key=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    symbol = Column(String(10))
    rsi = Column(Integer)
    ema = Column(Integer)
    macd = Column(Integer)
    atr = Column(Integer)
    stochastic_oscillator = Column(Integer)
    bollinger_bands = Column(Integer)
    adx = Column(Integer)
    period_type = Column(String(10))
    period_number = Column(Integer)
