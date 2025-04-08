from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, 
    ForeignKey, Text, JSON, Table, Enum
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()

# Association table for many-to-many relationship between users and watchlists
user_watchlist_association = Table(
    'user_watchlist_association', 
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('watchlist_id', Integer, ForeignKey('watchlists.id'), primary_key=True)
)

class SignalType(enum.Enum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"

class ActionType(enum.Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"
    SHORT = "short"
    COVER = "cover"

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    portfolios = relationship("Portfolio", back_populates="user")
    watchlists = relationship(
        "Watchlist", 
        secondary=user_watchlist_association,
        back_populates="users"
    )
    analysis_requests = relationship("AnalysisRequest", back_populates="user")
    trades = relationship("Trade", back_populates="user")

class Portfolio(Base):
    __tablename__ = 'portfolios'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    cash_balance = Column(Float, default=0.0)
    margin_requirement = Column(Float, default=0.0)
    margin_used = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="portfolios")
    positions = relationship("Position", back_populates="portfolio")
    
    def calculate_total_value(self):
        """Calculate the total value of the portfolio including cash and positions"""
        position_value = sum(position.current_value for position in self.positions)
        return self.cash_balance + position_value

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    ticker = Column(String(20), nullable=False)
    long_shares = Column(Integer, default=0)
    short_shares = Column(Integer, default=0)
    long_cost_basis = Column(Float, default=0.0)
    short_cost_basis = Column(Float, default=0.0)
    short_margin_used = Column(Float, default=0.0)
    last_price = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    
    @property
    def current_value(self):
        """Calculate the current value of the position"""
        if not self.last_price:
            return 0
        
        long_value = self.long_shares * self.last_price
        # For short positions, the value is negative and depends on the difference
        # between the current price and the short price
        short_value = self.short_shares * (self.short_cost_basis - self.last_price)
        return long_value + short_value

class Watchlist(Base):
    __tablename__ = 'watchlists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship(
        "User", 
        secondary=user_watchlist_association,
        back_populates="watchlists"
    )
    stocks = relationship("WatchlistStock", back_populates="watchlist")

class WatchlistStock(Base):
    __tablename__ = 'watchlist_stocks'
    
    id = Column(Integer, primary_key=True)
    watchlist_id = Column(Integer, ForeignKey('watchlists.id'), nullable=False)
    ticker = Column(String(20), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    watchlist = relationship("Watchlist", back_populates="stocks")

class AnalysisRequest(Base):
    __tablename__ = 'analysis_requests'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    ticker = Column(String(20), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    model_name = Column(String(100))
    model_provider = Column(String(100))
    analysts = Column(JSON)  # Stores a list of selected analysts
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="analysis_requests")
    results = relationship("AnalysisResult", back_populates="analysis_request")

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True)
    analysis_request_id = Column(Integer, ForeignKey('analysis_requests.id'), nullable=False)
    analyst_name = Column(String(100), nullable=False)
    ticker = Column(String(20), nullable=False)
    signal = Column(Enum(SignalType))
    confidence = Column(Float)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    analysis_request = relationship("AnalysisRequest", back_populates="results")

class Trade(Base):
    __tablename__ = 'trades'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    portfolio_id = Column(Integer, ForeignKey('portfolios.id'), nullable=False)
    ticker = Column(String(20), nullable=False)
    action = Column(Enum(ActionType), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    notes = Column(Text)
    
    # Relationships
    user = relationship("User", back_populates="trades")
    portfolio = relationship("Portfolio")

class FinancialDataCache(Base):
    __tablename__ = 'financial_data_cache'
    
    id = Column(Integer, primary_key=True)
    ticker = Column(String(20), nullable=False)
    data_type = Column(String(50), nullable=False)  # prices, financial_metrics, etc.
    time_period = Column(String(50))  # daily, annual, quarterly, etc.
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    data = Column(JSON, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Composite index for efficient lookups
    __table_args__ = (
        # Index for faster cache lookup
        # Needs SQLAlchemy 1.4+
        # Index('cache_lookup_idx', ticker, data_type, time_period),
    )