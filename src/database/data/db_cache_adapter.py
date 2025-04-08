"""
Database-backed cache adapter that integrates with the original cache interface.
This allows the existing code to work with the new database cache.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any

from sqlalchemy.orm import Session

from .cache import Cache
from database.repositories import FinancialDataCacheRepository, DataCacheCreate


class DatabaseBackedCache(Cache):
    """
    Database-backed implementation of the Cache interface.
    This adapter keeps the same API but stores data in the database.
    """

    def __init__(self, db: Session):
        super().__init__()
        self.db = db
        self.cache_repo = FinancialDataCacheRepository(None, db)

    def _convert_to_datetime(self, date_str: Optional[str]) -> Optional[datetime]:
        """Convert string date to datetime object"""
        if not date_str:
            return None
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            # Try different format if ISO format fails
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                return None

    def get_prices(self, ticker: str) -> List[Dict[str, Any]]:
        """Get cached price data if available."""
        cache_entry = self.cache_repo.get_by_ticker_and_type(ticker, "prices")
        if cache_entry:
            return cache_entry.data
        return None

    def set_prices(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new price data to cache."""
        # Get date range from data
        dates = [item.get("time") for item in data if "time" in item]
        start_date = min(dates) if dates else None
        end_date = max(dates) if dates else None
        
        # Convert to datetime objects
        start_dt = self._convert_to_datetime(start_date)
        end_dt = self._convert_to_datetime(end_date)
        
        # Update or create cache entry
        self.cache_repo.update_or_create(
            ticker=ticker,
            data_type="prices",
            time_period="daily",
            data=data,
            start_date=start_dt,
            end_date=end_dt
        )

    def get_financial_metrics(self, ticker: str) -> List[Dict[str, Any]]:
        """Get cached financial metrics if available."""
        cache_entry = self.cache_repo.get_by_ticker_and_type(ticker, "financial_metrics")
        if cache_entry:
            return cache_entry.data
        return None

    def set_financial_metrics(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new financial metrics to cache."""
        # Get date range from data
        report_periods = [item.get("report_period") for item in data if "report_period" in item]
        start_date = min(report_periods) if report_periods else None
        end_date = max(report_periods) if report_periods else None
        
        # Convert to datetime objects
        start_dt = self._convert_to_datetime(start_date)
        end_dt = self._convert_to_datetime(end_date)
        
        # Update or create cache entry
        self.cache_repo.update_or_create(
            ticker=ticker,
            data_type="financial_metrics",
            data=data,
            start_date=start_dt,
            end_date=end_dt
        )

    def get_line_items(self, ticker: str) -> List[Dict[str, Any]]:
        """Get cached line items if available."""
        cache_entry = self.cache_repo.get_by_ticker_and_type(ticker, "line_items")
        if cache_entry:
            return cache_entry.data
        return None

    def set_line_items(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new line items to cache."""
        # Get date range from data
        report_periods = [item.get("report_period") for item in data if "report_period" in item]
        start_date = min(report_periods) if report_periods else None
        end_date = max(report_periods) if report_periods else None
        
        # Convert to datetime objects
        start_dt = self._convert_to_datetime(start_date)
        end_dt = self._convert_to_datetime(end_date)
        
        # Update or create cache entry
        self.cache_repo.update_or_create(
            ticker=ticker,
            data_type="line_items",
            data=data,
            start_date=start_dt,
            end_date=end_dt
        )

    def get_insider_trades(self, ticker: str) -> List[Dict[str, Any]]:
        """Get cached insider trades if available."""
        cache_entry = self.cache_repo.get_by_ticker_and_type(ticker, "insider_trades")
        if cache_entry:
            return cache_entry.data
        return None

    def set_insider_trades(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new insider trades to cache."""
        # Get date range from data
        dates = [item.get("filing_date") for item in data if "filing_date" in item]
        start_date = min(dates) if dates else None
        end_date = max(dates) if dates else None
        
        # Convert to datetime objects
        start_dt = self._convert_to_datetime(start_date)
        end_dt = self._convert_to_datetime(end_date)
        
        # Update or create cache entry
        self.cache_repo.update_or_create(
            ticker=ticker,
            data_type="insider_trades",
            data=data,
            start_date=start_dt,
            end_date=end_dt
        )

    def get_company_news(self, ticker: str) -> List[Dict[str, Any]]:
        """Get cached company news if available."""
        cache_entry = self.cache_repo.get_by_ticker_and_type(ticker, "company_news")
        if cache_entry:
            return cache_entry.data
        return None

    def set_company_news(self, ticker: str, data: List[Dict[str, Any]]):
        """Append new company news to cache."""
        # Get date range from data
        dates = [item.get("date") for item in data if "date" in item]
        start_date = min(dates) if dates else None
        end_date = max(dates) if dates else None
        
        # Convert to datetime objects
        start_dt = self._convert_to_datetime(start_date)
        end_dt = self._convert_to_datetime(end_date)
        
        # Update or create cache entry
        self.cache_repo.update_or_create(
            ticker=ticker,
            data_type="company_news",
            data=data,
            start_date=start_dt,
            end_date=end_dt
        )


def get_db_cache(db: Session) -> DatabaseBackedCache:
    """
    Get a database-backed cache instance.
    """
    return DatabaseBackedCache(db)