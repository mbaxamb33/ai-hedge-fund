from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from ..models import Portfolio, Position
from .base import BaseRepository
from pydantic import BaseModel

class PortfolioCreate(BaseModel):
    user_id: int
    name: str
    description: Optional[str] = None
    cash_balance: float = 0.0
    margin_requirement: float = 0.0

class PortfolioUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    cash_balance: Optional[float] = None
    margin_requirement: Optional[float] = None
    margin_used: Optional[float] = None

class PositionCreate(BaseModel):
    portfolio_id: int
    ticker: str
    long_shares: int = 0
    short_shares: int = 0
    long_cost_basis: float = 0.0
    short_cost_basis: float = 0.0
    short_margin_used: float = 0.0
    last_price: Optional[float] = None

class PositionUpdate(BaseModel):
    long_shares: Optional[int] = None
    short_shares: Optional[int] = None
    long_cost_basis: Optional[float] = None
    short_cost_basis: Optional[float] = None
    short_margin_used: Optional[float] = None
    last_price: Optional[float] = None

class PortfolioRepository(BaseRepository[Portfolio, PortfolioCreate, PortfolioUpdate]):
    """
    Repository for Portfolio operations
    """
    
    def get_by_user_id(self, user_id: int) -> List[Portfolio]:
        """
        Get all portfolios for a user
        """
        return self.db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    
    def get_portfolio_with_positions(self, portfolio_id: int) -> Optional[Portfolio]:
        """
        Get portfolio with all positions eager loaded
        """
        return (
            self.db.query(Portfolio)
            .filter(Portfolio.id == portfolio_id)
            .first()
        )

class PositionRepository(BaseRepository[Position, PositionCreate, PositionUpdate]):
    """
    Repository for Position operations
    """
    
    def get_by_portfolio_and_ticker(self, portfolio_id: int, ticker: str) -> Optional[Position]:
        """
        Get a position by portfolio ID and ticker
        """
        return (
            self.db.query(Position)
            .filter(Position.portfolio_id == portfolio_id, Position.ticker == ticker)
            .first()
        )
    
    def get_all_by_portfolio(self, portfolio_id: int) -> List[Position]:
        """
        Get all positions for a portfolio
        """
        return self.db.query(Position).filter(Position.portfolio_id == portfolio_id).all()
    
    def update_position_price(self, position_id: int, price: float) -> Position:
        """
        Update the last price of a position
        """
        position = self.get(position_id)
        if position:
            position.last_price = price
            self.db.commit()
            self.db.refresh(position)
        return position