from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class NewsStatus(str, Enum):
    DRAFT = "DRAFT"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"
    DELETED = "DELETED"

class CommentStatus(str, Enum):
    ACTIVE = "ACTIVE"
    MODERATED = "MODERATED"
    DELETED = "DELETED"

class LikeType(str, Enum):
    LIKE = "LIKE"
    LOVE = "LOVE"
    HELPFUL = "HELPFUL"
    INSIGHTFUL = "INSIGHTFUL"

class SharePlatform(str, Enum):
    FACEBOOK = "FACEBOOK"
    TWITTER = "TWITTER"
    LINKEDIN = "LINKEDIN"
    WHATSAPP = "WHATSAPP"
    EMAIL = "EMAIL"
    COPY_LINK = "COPY_LINK"

# Base Models
class NewsPostBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="News post title")
    content: str = Field(..., min_length=1, description="News post content")
    summary: Optional[str] = Field(None, max_length=500, description="News post summary")
    category: Optional[str] = Field(None, max_length=100, description="News category")
    tags: Optional[List[str]] = Field(None, description="List of tags")
    featured_image: Optional[str] = Field(None, max_length=500, description="Featured image URL")
    status: NewsStatus = Field(default=NewsStatus.DRAFT, description="News post status")
    publish_date: Optional[datetime] = Field(None, description="Publish date")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date")
    is_featured: bool = Field(default=False, description="Is featured news")
    is_top_story: bool = Field(default=False, description="Is top story")
    seo_title: Optional[str] = Field(None, max_length=255, description="SEO title")
    seo_description: Optional[str] = Field(None, max_length=500, description="SEO description")
    seo_keywords: Optional[str] = Field(None, max_length=500, description="SEO keywords")
    meta_data: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

class NewsPostCreate(NewsPostBase):
    author_id: int = Field(..., description="Author user ID")
    business_user_id: Optional[int] = Field(None, description="Business user ID")

class NewsPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    content: Optional[str] = Field(None, min_length=1)
    summary: Optional[str] = Field(None, max_length=500)
    category: Optional[str] = Field(None, max_length=100)
    tags: Optional[List[str]] = None
    featured_image: Optional[str] = Field(None, max_length=500)
    status: Optional[NewsStatus] = None
    publish_date: Optional[datetime] = None
    expiry_date: Optional[datetime] = None
    is_featured: Optional[bool] = None
    is_top_story: Optional[bool] = None
    seo_title: Optional[str] = Field(None, max_length=255)
    seo_description: Optional[str] = Field(None, max_length=500)
    seo_keywords: Optional[str] = Field(None, max_length=500)
    meta_data: Optional[Dict[str, Any]] = None

class NewsPostResponse(NewsPostBase):
    news_id: int = Field(..., description="News post ID")
    author_id: int = Field(..., description="Author user ID")
    business_user_id: Optional[int] = Field(None, description="Business user ID")
    view_count: int = Field(..., description="View count")
    like_count: int = Field(..., description="Like count")
    share_count: int = Field(..., description="Share count")
    added_by: int = Field(..., description="Added by user ID")
    added_on: datetime = Field(..., description="Added on timestamp")
    updated_by: Optional[int] = Field(None, description="Updated by user ID")
    updated_on: Optional[datetime] = Field(None, description="Updated on timestamp")
    
    # Author information
    author_name: Optional[str] = Field(None, description="Author name")
    business_name: Optional[str] = Field(None, description="Business name")
    
    class Config:
        from_attributes = True

# Comment Models
class NewsCommentBase(BaseModel):
    content: str = Field(..., min_length=1, description="Comment content")
    parent_comment_id: Optional[int] = Field(None, description="Parent comment ID for replies")

class NewsCommentCreate(NewsCommentBase):
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")

class NewsCommentUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1)
    status: Optional[CommentStatus] = None

class NewsCommentResponse(NewsCommentBase):
    comment_id: int = Field(..., description="Comment ID")
    news_id: int = Field(..., description="News post ID")
    user_id: int = Field(..., description="User ID")
    status: CommentStatus = Field(..., description="Comment status")
    like_count: int = Field(..., description="Like count")
    added_by: int = Field(..., description="Added by user ID")
    added_on: datetime = Field(..., description="Added on timestamp")
    updated_by: Optional[int] = Field(None, description="Updated by user ID")
    updated_on: Optional[datetime] = Field(None, description="Updated on timestamp")
    
    # User information
    user_name: Optional[str] = Field(None, description="User name")
    user_avatar: Optional[str] = Field(None, description="User avatar")
    
    # Replies
    replies: List['NewsCommentResponse'] = Field(default=[], description="Comment replies")
    
    class Config:
        from_attributes = True

# Like Models
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
    
    class Config:
        from_attributes = True

# Share Models
class NewsShareBase(BaseModel):
    share_platform: SharePlatform = Field(..., description="Share platform")
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
    
    class Config:
        from_attributes = True

# Query Models
class NewsPostQueryParams(BaseModel):
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=10, ge=1, le=100, description="Page size")
    category: Optional[str] = Field(None, description="Filter by category")
    status: Optional[NewsStatus] = Field(None, description="Filter by status")
    author_id: Optional[int] = Field(None, description="Filter by author")
    business_user_id: Optional[int] = Field(None, description="Filter by business")
    is_featured: Optional[bool] = Field(None, description="Filter featured news")
    is_top_story: Optional[bool] = Field(None, description="Filter top stories")
    search: Optional[str] = Field(None, description="Search in title and content")
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    sort_by: str = Field(default="added_on", description="Sort field")
    sort_order: str = Field(default="desc", description="Sort order (asc/desc)")

# Response Models
class NewsPostListResponse(BaseModel):
    news_posts: List[NewsPostResponse] = Field(..., description="List of news posts")
    total_count: int = Field(..., description="Total count")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    total_pages: int = Field(..., description="Total pages")

class NewsPostDetailResponse(BaseModel):
    news_post: NewsPostResponse = Field(..., description="News post details")
    comments: List[NewsCommentResponse] = Field(default=[], description="Comments")
    likes: List[NewsLikeResponse] = Field(default=[], description="Likes")
    shares: List[NewsShareResponse] = Field(default=[], description="Shares")
    related_posts: List[NewsPostResponse] = Field(default=[], description="Related posts")

# Analytics Models
class NewsPostAnalytics(BaseModel):
    news_id: int = Field(..., description="News post ID")
    title: str = Field(..., description="News post title")
    view_count: int = Field(..., description="View count")
    like_count: int = Field(..., description="Like count")
    share_count: int = Field(..., description="Share count")
    comment_count: int = Field(..., description="Comment count")
    engagement_rate: float = Field(..., description="Engagement rate")
    created_date: datetime = Field(..., description="Creation date")

# Forward references for nested models
# Note: In Pydantic v2, model_rebuild() is not needed
