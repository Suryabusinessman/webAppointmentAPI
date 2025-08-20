from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status as http_status
from app.models.NewsModules.newspost import NewsShare
from app.models.UserModules.users import User
from app.models.NewsModules.newspost import NewsPost
import logging

logger = logging.getLogger(__name__)

class NewsShareRepository:
    """Repository for NewsShare operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, share_id: int) -> Optional[NewsShare]:
        """Get share by ID"""
        try:
            return self.db.query(NewsShare).filter(NewsShare.share_id == share_id).first()
        except Exception as e:
            logger.error(f"Error getting share by ID {share_id}: {str(e)}")
            return None
    
    def get_shares_by_news_id(self, news_id: int) -> List[NewsShare]:
        """Get all shares for a news post with user information"""
        try:
            return self.db.query(NewsShare)\
                .options(joinedload(NewsShare.user))\
                .filter(NewsShare.news_id == news_id)\
                .order_by(desc(NewsShare.added_on))\
                .all()
        except Exception as e:
            logger.error(f"Error getting shares for news {news_id}: {str(e)}")
            return []
    
    def create_share(self, share_data: Dict[str, Any]) -> NewsShare:
        """Create a new share"""
        try:
            share = NewsShare(**share_data)
            self.db.add(share)
            self.db.commit()
            self.db.refresh(share)
            
            # Update share count in news post
            self._update_share_count(share_data['news_id'])
            
            return share
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating share: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create share"
            )
    
    def get_user_shares(self, user_id: int, limit: int = 20) -> List[NewsShare]:
        """Get shares by a specific user"""
        try:
            return self.db.query(NewsShare)\
                .options(
                    joinedload(NewsShare.news_post),
                    joinedload(NewsShare.user)
                )\
                .filter(NewsShare.user_id == user_id)\
                .order_by(desc(NewsShare.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting shares for user {user_id}: {str(e)}")
            return []
    
    def get_share_analytics(self, news_id: int) -> Dict[str, Any]:
        """Get share analytics for a news post"""
        try:
            shares = self.get_shares_by_news_id(news_id)
            
            # Count by platform
            platform_counts = {}
            for share in shares:
                platform = share.share_platform
                platform_counts[platform] = platform_counts.get(platform, 0) + 1
            
            return {
                "total_shares": len(shares),
                "platform_breakdown": platform_counts,
                "most_popular_platform": max(platform_counts.items(), key=lambda x: x[1])[0] if platform_counts else None
            }
        except Exception as e:
            logger.error(f"Error getting share analytics for news {news_id}: {str(e)}")
            return {"total_shares": 0, "platform_breakdown": {}, "most_popular_platform": None}
    
    def get_platform_shares(self, platform: str, limit: int = 20) -> List[NewsShare]:
        """Get shares by platform"""
        try:
            return self.db.query(NewsShare)\
                .options(
                    joinedload(NewsShare.news_post),
                    joinedload(NewsShare.user)
                )\
                .filter(NewsShare.share_platform == platform)\
                .order_by(desc(NewsShare.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting shares for platform {platform}: {str(e)}")
            return []
    
    def _update_share_count(self, news_id: int):
        """Update share count in news post"""
        try:
            share_count = self.db.query(NewsShare)\
                .filter(NewsShare.news_id == news_id)\
                .count()
            
            news_post = self.db.query(NewsPost).filter(NewsPost.news_id == news_id).first()
            if news_post:
                news_post.share_count = share_count
                self.db.commit()
        except Exception as e:
            logger.error(f"Error updating share count for news {news_id}: {str(e)}")
