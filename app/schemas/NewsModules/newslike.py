from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class LikeType(str, Enum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    HELPFUL = "HELPFUL"
    INSIGHTFUL = "INSIGHTFUL"

# Base Models
class NewsLikeBase(BaseModel):
    like_type: LikeType = Field(default=LikeType.LIKE, description="Type of like")

class NewsLikeCreate(NewsLikeBase):
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")

class NewsLikeResponse(NewsLikeBase):
    like_id: int = Field(..., description="Like ID")
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")
    added_on: datetime = Field(..., description="Added on timestamp")
    
    # User information
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")
    
    # News information
    news_title: Optional[str] = Field(None, description="News title")
    
    class Config:
        from_attributes = True
