from fastapi import HTTPException, status as http_status
from app.repositories.NewsModules.newscomments import NewsCommentRepository
from app.schemas.NewsModules.newscomments import NewsCommentCreate, NewsCommentUpdate, NewsCommentResponse
from app.models.NewsModules.newspost import NewsComment
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

class NewsCommentService:
    """Service for NewsComment operations"""
    
    def __init__(self, comment_repository: NewsCommentRepository, security_key: str):
        self.comment_repository = comment_repository
        self.security_key = security_key

    def get_comments_by_news_id(self, news_id: int, security_key: str):
        """Get all comments for a specific news post."""
        comments = self.comment_repository.get_comments_by_news_id(news_id)
        return {
            "status": "success",
            "message": f"Retrieved {len(comments)} comments for news post {news_id}",
            "data": comments
        }

    def create_comment(self, comment_data: NewsCommentCreate, security_key: str, added_by: int):
        """Create a new comment."""
        # Convert Pydantic model to dict
        comment_dict = comment_data.model_dump()
        comment_dict['added_by'] = added_by
        
        new_comment = self.comment_repository.create_comment(comment_dict, added_by)
        if not new_comment:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create comment."
            )
        return {
            "status": "success",
            "message": "Comment created successfully.",
            "data": new_comment
        }

    def update_comment(self, comment_id: int, comment_data: NewsCommentUpdate, security_key: str, modified_by: int):
        """Update an existing comment."""
        # Convert Pydantic model to dict
        update_dict = comment_data.model_dump(exclude_unset=True)
        
        updated_comment = self.comment_repository.update_comment(comment_id, update_dict, modified_by)
        if not updated_comment:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found."
            )
        return {
            "status": "success",
            "message": "Comment updated successfully.",
            "data": updated_comment
        }

    def delete_comment(self, comment_id: int, security_key: str, deleted_by: int):
        """Delete a comment (soft delete)."""
        success = self.comment_repository.delete_comment(comment_id)
        if not success:
            raise HTTPException(
                status_code=http_status.HTTP_404_NOT_FOUND,
                detail=f"Comment with ID {comment_id} not found."
            )
        return {
            "status": "success",
            "message": "Comment deleted successfully.",
            "data": {"comment_id": comment_id}
        }

    def get_replies(self, parent_comment_id: int, security_key: str):
        """Get replies to a comment."""
        replies = self.comment_repository.get_replies(parent_comment_id)
        return {
            "status": "success",
            "message": f"Retrieved {len(replies)} replies for comment {parent_comment_id}",
            "data": replies
        }

    def get_user_comments(self, user_id: int, security_key: str, limit: int = 20):
        """Get comments by a specific user."""
        comments = self.comment_repository.get_user_comments(user_id, limit)
        return {
            "status": "success",
            "message": f"Retrieved {len(comments)} comments for user {user_id}",
            "data": comments
        }
