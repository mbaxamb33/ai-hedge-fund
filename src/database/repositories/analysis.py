from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from ..models import AnalysisRequest, AnalysisResult, SignalType
from .base import BaseRepository
from pydantic import BaseModel

class AnalysisRequestCreate(BaseModel):
    user_id: int
    ticker: str
    start_date: datetime
    end_date: datetime
    model_name: Optional[str] = None
    model_provider: Optional[str] = None
    analysts: Optional[List[str]] = None

class AnalysisRequestUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None

class AnalysisResultCreate(BaseModel):
    analysis_request_id: int
    analyst_name: str
    ticker: str
    signal: SignalType
    confidence: float
    reasoning: Optional[str] = None

class AnalysisResultUpdate(BaseModel):
    signal: Optional[SignalType] = None
    confidence: Optional[float] = None
    reasoning: Optional[str] = None

class AnalysisRequestRepository(BaseRepository[AnalysisRequest, AnalysisRequestCreate, AnalysisRequestUpdate]):
    """
    Repository for Analysis Request operations
    """
    
    def get_by_user_id(self, user_id: int, skip: int = 0, limit: int = 100) -> List[AnalysisRequest]:
        """
        Get all analysis requests for a user
        """
        return (
            self.db.query(AnalysisRequest)
            .filter(AnalysisRequest.user_id == user_id)
            .order_by(AnalysisRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_by_ticker(self, ticker: str, skip: int = 0, limit: int = 100) -> List[AnalysisRequest]:
        """
        Get all analysis requests for a ticker
        """
        return (
            self.db.query(AnalysisRequest)
            .filter(AnalysisRequest.ticker == ticker)
            .order_by(AnalysisRequest.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_pending_requests(self, limit: int = 10) -> List[AnalysisRequest]:
        """
        Get pending analysis requests
        """
        return (
            self.db.query(AnalysisRequest)
            .filter(AnalysisRequest.status == "pending")
            .order_by(AnalysisRequest.created_at)
            .limit(limit)
            .all()
        )
    
    def update_status(self, request_id: int, status: str, completed_at: Optional[datetime] = None) -> AnalysisRequest:
        """
        Update the status of an analysis request
        """
        request = self.get(request_id)
        if request:
            request.status = status
            if completed_at:
                request.completed_at = completed_at
            elif status == "completed":
                request.completed_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(request)
        return request

class AnalysisResultRepository(BaseRepository[AnalysisResult, AnalysisResultCreate, AnalysisResultUpdate]):
    """
    Repository for Analysis Result operations
    """
    
    def get_by_request_id(self, request_id: int) -> List[AnalysisResult]:
        """
        Get all results for an analysis request
        """
        return (
            self.db.query(AnalysisResult)
            .filter(AnalysisResult.analysis_request_id == request_id)
            .all()
        )
    
    def get_by_ticker_and_analyst(self, ticker: str, analyst_name: str, limit: int = 1) -> List[AnalysisResult]:
        """
        Get the most recent analysis results for a ticker and analyst
        """
        return (
            self.db.query(AnalysisResult)
            .filter(
                AnalysisResult.ticker == ticker,
                AnalysisResult.analyst_name == analyst_name
            )
            .order_by(AnalysisResult.created_at.desc())
            .limit(limit)
            .all()
        )