from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class CommentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MODERATED = "MODERATED"
    DELETED = "DELETED"

# Base Models
class NewsCommentBase(BaseModel):
    content: str = Field(..., min_length=1, description="Comment content")
    parent_comment_id: Optional[int] = Field(None, description="Parent comment ID for replies")

class NewsCommentCreate(NewsCommentBase):
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")

class NewsCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)

class NewsCommentResponse(NewsCommentBase):
    comment_id: int = Field(..., description="Comment ID")
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")
    parent_comment_id: Optional[int] = Field(None, description="Parent comment ID")
    status: CommentStatus = Field(..., description="Comment status")
    like_count: int = Field(..., description="Like count")
    added_by: int = Field(..., description="Added by user ID")
    added_on: datetime = Field(..., description="Added on timestamp")
    updated_by: Optional[int] = Field(None, description="Updated by user ID")
    updated_on: Optional[datetime] = Field(None, description="Updated on timestamp")
    
    # User information
    user_name: Optional[str] = Field(None, description="User name")
    user_email: Optional[str] = Field(None, description="User email")
    
    # News information
    news_title: Optional[str] = Field(None, description="News title")
    
    # Reply information
    replies: Optional[List['NewsCommentResponse']] = Field(None, description="Replies to this comment")
    
    class Config:
        from_attributes = True

# For circular imports - not needed in this Pydantic version
