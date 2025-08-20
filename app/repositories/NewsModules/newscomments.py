from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, desc, asc, func
from fastapi import HTTPException, status as http_status
from app.models.NewsModules.newspost import NewsComment
from app.models.UserModules.users import User
from app.models.NewsModules.newspost import NewsPost
import logging

logger = logging.getLogger(__name__)

class NewsCommentRepository:
    """Repository for NewsComment operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_by_id(self, comment_id: int) -> Optional[NewsComment]:
        """Get comment by ID"""
        try:
            return self.db.query(NewsComment).filter(NewsComment.comment_id == comment_id).first()
        except Exception as e:
            logger.error(f"Error getting comment by ID {comment_id}: {str(e)}")
            return None
    
    def get_comments_by_news_id(self, news_id: int) -> List[NewsComment]:
        """Get all comments for a news post with user information"""
        try:
            return self.db.query(NewsComment)\
                .options(
                    joinedload(NewsComment.user),
                    joinedload(NewsComment.added_by_user),
                    joinedload(NewsComment.updated_by_user),
                    joinedload(NewsComment.news_post)
                )\
                .filter(
                    and_(
                        NewsComment.news_id == news_id,
                        NewsComment.status == "ACTIVE"
                    )
                )\
                .order_by(asc(NewsComment.added_on))\
                .all()
        except Exception as e:
            logger.error(f"Error getting comments for news {news_id}: {str(e)}")
            return []
    
    def create_comment(self, comment_data: Dict[str, Any], user_id: int) -> NewsComment:
        """Create a new comment"""
        try:
            # Set default values
            comment_data['status'] = comment_data.get('status', 'ACTIVE')
            comment_data['like_count'] = comment_data.get('like_count', 0)
            comment_data['added_by'] = user_id
            
            # Ensure parent_comment_id is None if not provided or if it's 0
            if 'parent_comment_id' in comment_data and (comment_data['parent_comment_id'] == 0 or comment_data['parent_comment_id'] == ''):
                comment_data['parent_comment_id'] = None
            
            comment = NewsComment(**comment_data)
            self.db.add(comment)
            self.db.commit()
            self.db.refresh(comment)
            
            # Update comment count in news post
            self._update_comment_count(comment_data['news_id'])
            
            return comment
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating comment: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment"
            )
    
    def update_comment(self, comment_id: int, update_data: Dict[str, Any], user_id: int) -> Optional[NewsComment]:
        """Update a comment"""
        try:
            comment = self.db.query(NewsComment).filter(NewsComment.comment_id == comment_id).first()
            if not comment:
                return None
            
            update_data['updated_by'] = user_id
            for field, value in update_data.items():
                if hasattr(comment, field):
                    setattr(comment, field, value)
            
            self.db.commit()
            self.db.refresh(comment)
            return comment
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating comment {comment_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update comment"
            )
    
    def delete_comment(self, comment_id: int) -> bool:
        """Delete a comment (soft delete)"""
        try:
            comment = self.db.query(NewsComment).filter(NewsComment.comment_id == comment_id).first()
            if not comment:
                return False
            
            comment.status = "DELETED"
            self.db.commit()
            
            # Update comment count in news post
            self._update_comment_count(comment.news_id)
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting comment {comment_id}: {str(e)}")
            return False
    
    def get_replies(self, parent_comment_id: int) -> List[NewsComment]:
        """Get replies to a comment"""
        try:
            return self.db.query(NewsComment)\
                .options(joinedload(NewsComment.user))\
                .filter(
                    and_(
                        NewsComment.parent_comment_id == parent_comment_id,
                        NewsComment.status == "ACTIVE"
                    )
                )\
                .order_by(asc(NewsComment.added_on))\
                .all()
        except Exception as e:
            logger.error(f"Error getting replies for comment {parent_comment_id}: {str(e)}")
            return []
    
    def _update_comment_count(self, news_id: int):
        """Update comment count in news post"""
        try:
            comment_count = self.db.query(NewsComment)\
                .filter(
                    and_(
                        NewsComment.news_id == news_id,
                        NewsComment.status == "ACTIVE"
                    )
                )\
                .count()
            
            news_post = self.db.query(NewsPost).filter(NewsPost.news_id == news_id).first()
            if news_post:
                news_post.comment_count = comment_count
                self.db.commit()
        except Exception as e:
            logger.error(f"Error updating comment count for news {news_id}: {str(e)}")
    
    def get_user_comments(self, user_id: int, limit: int = 20) -> List[NewsComment]:
        """Get comments by a specific user"""
        try:
            return self.db.query(NewsComment)\
                .options(
                    joinedload(NewsComment.news_post),
                    joinedload(NewsComment.user)
                )\
                .filter(
                    and_(
                        NewsComment.user_id == user_id,
                        NewsComment.status == "ACTIVE"
                    )
                )\
                .order_by(desc(NewsComment.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting comments for user {user_id}: {str(e)}")
            return []
