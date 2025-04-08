from typing import Optional, Dict, Any, List
from datetime import datetime
from sqlalchemy import and_
from sqlalchemy.orm import Session
from ..models import FinancialDataCache
from .base import BaseRepository
from pydantic import BaseModel

class DataCacheCreate(BaseModel):
    ticker: str
    data_type: str
    time_period: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    data: Dict[str, Any]

class DataCacheUpdate(BaseModel):
    data: Optional[Dict[str, Any]] = None
    end_date: Optional[datetime] = None
    last_updated: Optional[datetime] = None

class FinancialDataCacheRepository(BaseRepository[FinancialDataCache, DataCacheCreate, DataCacheUpdate]):
    """
    Repository for Financial Data Cache operations
    """
    
    def get_by_ticker_and_type(
        self, 
        ticker: str, 
        data_type: str, 
        time_period: Optional[str] = None
    ) -> Optional[FinancialDataCache]:
        """
        Get cached data by ticker and type
        """
        query = (
            self.db.query(FinancialDataCache)
            .filter(
                FinancialDataCache.ticker == ticker,
                FinancialDataCache.data_type == data_type
            )
        )
        
        if time_period:
            query = query.filter(FinancialDataCache.time_period == time_period)
            
        return query.order_by(FinancialDataCache.last_updated.desc()).first()
    
    def get_by_date_range(
        self,
        ticker: str,
        data_type: str,
        start_date: datetime,
        end_date: datetime,
        time_period: Optional[str] = None
    ) -> Optional[FinancialDataCache]:
        """
        Get cached data for a specific date range
        """
        query = (
            self.db.query(FinancialDataCache)
            .filter(
                FinancialDataCache.ticker == ticker,
                FinancialDataCache.data_type == data_type,
                FinancialDataCache.start_date <= start_date,
                FinancialDataCache.end_date >= end_date
            )
        )
        
        if time_period:
            query = query.filter(FinancialDataCache.time_period == time_period)
            
        return query.order_by(FinancialDataCache.last_updated.desc()).first()
    
    def update_or_create(
        self,
        ticker: str,
        data_type: str,
        data: Dict[str, Any],
        time_period: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> FinancialDataCache:
        """
        Update existing cache or create new entry
        """
        # Try to find existing cache entry
        existing = self.get_by_ticker_and_type(ticker, data_type, time_period)
        
        if existing:
            # Update existing entry
            update_data = {
                "data": data,
                "last_updated": datetime.utcnow()
            }
            
            if end_date:
                update_data["end_date"] = end_date
                
            return self.update(existing, update_data)
        else:
            # Create new entry
            new_cache = DataCacheCreate(
                ticker=ticker,
                data_type=data_type,
                time_period=time_period,
                start_date=start_date,
                end_date=end_date,
                data=data
            )
            return self.create(new_cache)
    
    def clear_old_cache(self, days: int = 30) -> int:
        """
        Delete cache entries older than specified days
        Returns number of deleted entries
        """
        cutoff_date = datetime.utcnow() - datetime.timedelta(days=days)
        result = (
            self.db.query(FinancialDataCache)
            .filter(FinancialDataCache.last_updated < cutoff_date)
            .delete()
        )
        self.db.commit()
        return result