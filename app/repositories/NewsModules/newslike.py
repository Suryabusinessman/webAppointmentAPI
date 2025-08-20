from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status as http_status
from app.models.NewsModules.newspost import NewsLike
from app.models.UserModules.users import User
from app.models.NewsModules.newspost import NewsPost
import logging

logger = logging.getLogger(__name__)

class NewsLikeRepository:
    """Repository for NewsLike operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, like_id: int) -> Optional[NewsLike]:
        """Get like by ID"""
        try:
            return self.db.query(NewsLike).filter(NewsLike.like_id == like_id).first()
        except Exception as e:
            logger.error(f"Error getting like by ID {like_id}: {str(e)}")
            return None
    
    def get_likes_by_news_id(self, news_id: int) -> List[NewsLike]:
        """Get all likes for a news post with user information"""
        try:
            return self.db.query(NewsLike)\
                .options(joinedload(NewsLike.user))\
                .filter(NewsLike.news_id == news_id)\
                .order_by(desc(NewsLike.added_on))\
                .all()
        except Exception as e:
            logger.error(f"Error getting likes for news {news_id}: {str(e)}")
            return []
    
    def create_like(self, like_data: Dict[str, Any]) -> NewsLike:
        """Create a new like or return existing like"""
        try:
            # Check if like already exists
            existing_like = self.check_user_like(like_data['news_id'], like_data['user_id'])
            if existing_like:
                # Return existing like if it already exists
                return existing_like
            
            # Create new like if it doesn't exist
            like = NewsLike(**like_data)
            self.db.add(like)
            self.db.commit()
            self.db.refresh(like)
            
            # Update like count in news post
            self._update_like_count(like_data['news_id'])
            
            return like
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating like: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create like"
            )
    
    def remove_like(self, news_id: int, user_id: int) -> bool:
        """Remove a like"""
        try:
            like = self.db.query(NewsLike)\
                .filter(
                    and_(
                        NewsLike.news_id == news_id,
                        NewsLike.user_id == user_id
                    )
                )\
                .first()
            
            if not like:
                return False
            
            self.db.delete(like)
            self.db.commit()
            
            # Update like count in news post
            self._update_like_count(news_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error removing like: {str(e)}")
            return False
    
    def get_user_likes(self, user_id: int, limit: int = 20) -> List[NewsLike]:
        """Get likes by a specific user"""
        try:
            return self.db.query(NewsLike)\
                .options(
                    joinedload(NewsLike.news_post),
                    joinedload(NewsLike.user)
                )\
                .filter(NewsLike.user_id == user_id)\
                .order_by(desc(NewsLike.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting likes for user {user_id}: {str(e)}")
            return []
    
    def check_user_like(self, news_id: int, user_id: int) -> Optional[NewsLike]:
        """Check if a user has liked a specific news post"""
        try:
            return self.db.query(NewsLike)\
                .filter(
                    and_(
                        NewsLike.news_id == news_id,
                        NewsLike.user_id == user_id
                    )
                )\
                .first()
        except Exception as e:
            logger.error(f"Error checking user like: {str(e)}")
            return None
    
    def get_like_analytics(self, news_id: int) -> Dict[str, Any]:
        """Get like analytics for a news post"""
        try:
            likes = self.get_likes_by_news_id(news_id)
            
            # Count by type
            type_counts = {}
            for like in likes:
                like_type = like.like_type
                type_counts[like_type] = type_counts.get(like_type, 0) + 1
            
            return {
                "total_likes": len(likes),
                "type_breakdown": type_counts,
                "most_popular_type": max(type_counts.items(), key=lambda x: x[1])[0] if type_counts else None
            }
        except Exception as e:
            logger.error(f"Error getting like analytics for news {news_id}: {str(e)}")
            return {"total_likes": 0, "type_breakdown": {}, "most_popular_type": None}
    
    def _update_like_count(self, news_id: int):
        """Update like count in news post"""
        try:
            like_count = self.db.query(NewsLike)\
                .filter(NewsLike.news_id == news_id)\
                .count()
            
            news_post = self.db.query(NewsPost).filter(NewsPost.news_id == news_id).first()
            if news_post:
                news_post.like_count = like_count
                self.db.commit()
        except Exception as e:
            logger.error(f"Error updating like count for news {news_id}: {str(e)}")
