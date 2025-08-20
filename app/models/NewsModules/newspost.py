from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Enum, JSON, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base

class NewsPost(Base):
    __tablename__ = "news_posts"
    
    news_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    content = Column(Text, nullable=False)
    summary = Column(String(500))
    author_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    business_user_id = Column(Integer, ForeignKey("business_users.business_user_id"))
    category = Column(String(100), index=True)
    tags = Column(JSON)  # Array of tags
    featured_image = Column(String(500))
    status = Column(Enum("DRAFT", "PUBLISHED", "ARCHIVED", "DELETED", name="news_status_enum"), default="DRAFT", index=True)
    publish_date = Column(DateTime)
    expiry_date = Column(DateTime)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    is_featured = Column(Boolean, default=False)
    is_top_story = Column(Boolean, default=False)
    seo_title = Column(String(255))
    seo_description = Column(String(500))
    seo_keywords = Column(String(500))
    meta_data = Column(JSON)  # Additional metadata
    added_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    added_on = Column(DateTime, server_default=func.now())
    updated_by = Column(Integer, ForeignKey("users.user_id"))
    updated_on = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    author = relationship("User", foreign_keys=[author_id], back_populates="news_posts")
    business_user = relationship("BusinessUser", back_populates="news_posts")
    added_by_user = relationship("User", foreign_keys=[added_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])
    
    # Additional relationships can be added here
    comments = relationship("NewsComment", back_populates="news_post", cascade="all, delete-orphan")
    likes = relationship("NewsLike", back_populates="news_post", cascade="all, delete-orphan")
    shares = relationship("NewsShare", back_populates="news_post", cascade="all, delete-orphan")

class NewsComment(Base):
    __tablename__ = "news_comments"
    
    comment_id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news_posts.news_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    parent_comment_id = Column(Integer, ForeignKey("news_comments.comment_id"))
    content = Column(Text, nullable=False)
    status = Column(Enum("ACTIVE", "MODERATED", "DELETED", name="comment_status_enum"), default="ACTIVE")
    like_count = Column(Integer, default=0)
    added_by = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    added_on = Column(DateTime, server_default=func.now())
    updated_by = Column(Integer, ForeignKey("users.user_id"))
    updated_on = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    news_post = relationship("NewsPost", back_populates="comments")
    user = relationship("User", foreign_keys=[user_id])
    parent_comment = relationship("NewsComment", remote_side=[comment_id])
    replies = relationship("NewsComment", back_populates="parent_comment")
    added_by_user = relationship("User", foreign_keys=[added_by])
    updated_by_user = relationship("User", foreign_keys=[updated_by])

class NewsLike(Base):
    __tablename__ = "news_likes"
    
    like_id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news_posts.news_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    like_type = Column(Enum("LIKE", "LOVE", "HELPFUL", "INSIGHTFUL", name="like_type_enum"), default="LIKE")
    added_on = Column(DateTime, server_default=func.now())
    
    # Relationships
    news_post = relationship("NewsPost", back_populates="likes")
    user = relationship("User")
    
    # Unique constraint to prevent duplicate likes
    __table_args__ = (UniqueConstraint('news_id', 'user_id', name='unique_news_user_like'),)

class NewsShare(Base):
    __tablename__ = "news_shares"
    
    share_id = Column(Integer, primary_key=True, index=True)
    news_id = Column(Integer, ForeignKey("news_posts.news_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    share_platform = Column(Enum("FACEBOOK", "TWITTER", "LINKEDIN", "WHATSAPP", "EMAIL", "COPY_LINK", name="share_platform_enum"))
    share_url = Column(String(500))
    added_on = Column(DateTime, server_default=func.now())
    
    # Relationships
    news_post = relationship("NewsPost", back_populates="shares")
    user = relationship("User")
