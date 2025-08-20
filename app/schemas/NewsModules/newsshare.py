from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class SharePlatform(str, Enum):
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"
    LINKEDIN = "LINKEDIN"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    COPY_LINK = "COPY_LINK"

# Base Models
class NewsShareBase(BaseModel):
    share_platform: SharePlatform = Field(..., description="Platform where news was shared")
    share_url: Optional[str] = Field(None, max_length=500, description="Share URL")

class NewsShareCreate(NewsShareBase):
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")

class NewsShareResponse(NewsShareBase):
    share_id: int = Field(..., description="Share ID")
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
