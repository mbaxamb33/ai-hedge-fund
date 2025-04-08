from typing import Optional, List
from sqlalchemy.orm import Session
from ..models import User
from .base import BaseRepository
from pydantic import BaseModel

class UserCreate(BaseModel):
    email: str
    password_hash: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserUpdate(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None

class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    Repository for User operations
    """
    
    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get a user by email
        """
        return self.db.query(User).filter(User.email == email).first()
    
    def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """
        Get all active users
        """
        return self.db.query(User).filter(User.is_active == True).offset(skip).limit(limit).all()