from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import Session, joinedload, aliased
from sqlalchemy import and_, or_, desc, asc, func, text
from fastapi import HTTPException, status as http_status
from app.models.NewsModules.newspost import NewsPost, NewsComment, NewsLike, NewsShare
from app.models.UserModules.users import User
from app.models.BusinessModules.businessmanuser import BusinessUser
from app.schemas.NewsModules.newspost import NewsPostQueryParams, NewsPostCreate, NewsPostUpdate
import logging

logger = logging.getLogger(__name__)

class NewsPostRepository:
    """Repository for NewsPost operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_news_post(self, news_data: Dict[str, Any], user_id: int) -> NewsPost:
        """Create a new news post"""
        try:
            news_data['added_by'] = user_id
            news_post = NewsPost(**news_data)
            self.db.add(news_post)
            self.db.commit()
            self.db.refresh(news_post)
            logger.info(f"Created news post with ID: {news_post.news_id}")
            return news_post
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating news post: {str(e)}")
            raise HTTPException(
                status_code=http_http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create news post"
            )
    
    def get_news_post_by_id(self, news_id: int) -> Optional[NewsPost]:
        """Get news post by ID with author and business information"""
        try:
            return self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user),
                    joinedload(NewsPost.added_by_user),
                    joinedload(NewsPost.updated_by_user)
                )\
                .filter(NewsPost.news_id == news_id)\
                .first()
        except Exception as e:
            logger.error(f"Error getting news post by ID {news_id}: {str(e)}")
            raise HTTPException(
                status_code=http_http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def get_all_news_posts(self, query_params: NewsPostQueryParams) -> Tuple[List[NewsPost], int]:
        """Get all news posts with filtering, pagination, and sorting"""
        try:
            query = self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user)
                )
            
            # Apply filters
            query = self._apply_filters(query, query_params)
            
            # Get total count before pagination
            total_count = query.count()
            
            # Apply sorting
            query = self._apply_sorting(query, query_params)
            
            # Apply pagination
            query = self._apply_pagination(query, query_params)
            
            news_posts = query.all()
            return news_posts, total_count
            
        except Exception as e:
            logger.error(f"Error getting all news posts: {str(e)}")
            raise HTTPException(
                status_code=http_http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def update_news_post(self, news_id: int, update_data: Dict[str, Any], user_id: int) -> Optional[NewsPost]:
        """Update news post"""
        try:
            news_post = self.get_news_post_by_id(news_id)
            if not news_post:
                return None
            
            update_data['updated_by'] = user_id
            for field, value in update_data.items():
                if hasattr(news_post, field):
                    setattr(news_post, field, value)
            
            self.db.commit()
            self.db.refresh(news_post)
            logger.info(f"Updated news post with ID: {news_id}")
            return news_post
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating news post {news_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update news post"
            )
    
    def delete_news_post(self, news_id: int) -> bool:
        """Delete news post (soft delete by setting status to DELETED)"""
        try:
            news_post = self.get_news_post_by_id(news_id)
            if not news_post:
                return False
            
            news_post.status = "DELETED"
            self.db.commit()
            logger.info(f"Deleted news post with ID: {news_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting news post {news_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete news post"
            )
    
    def increment_view_count(self, news_id: int) -> bool:
        """Increment view count for a news post"""
        try:
            news_post = self.db.query(NewsPost).filter(NewsPost.news_id == news_id).first()
            if news_post:
                news_post.view_count += 1
                self.db.commit()
                return True
            return False
        except Exception as e:
            logger.error(f"Error incrementing view count for news post {news_id}: {str(e)}")
            return False
    
    def get_featured_news(self, limit: int = 5) -> List[NewsPost]:
        """Get featured news posts"""
        try:
            return self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user)
                )\
                .filter(
                    and_(
                        NewsPost.is_featured == True,
                        NewsPost.status == "PUBLISHED"
                    )
                )\
                .order_by(desc(NewsPost.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting featured news: {str(e)}")
            return []
    
    def get_top_stories(self, limit: int = 5) -> List[NewsPost]:
        """Get top stories"""
        try:
            return self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user)
                )\
                .filter(
                    and_(
                        NewsPost.is_top_story == True,
                        NewsPost.status == "PUBLISHED"
                    )
                )\
                .order_by(desc(NewsPost.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting top stories: {str(e)}")
            return []
    
    def get_news_by_category(self, category: str, limit: int = 10) -> List[NewsPost]:
        """Get news posts by category"""
        try:
            return self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user)
                )\
                .filter(
                    and_(
                        NewsPost.category == category,
                        NewsPost.status == "PUBLISHED"
                    )
                )\
                .order_by(desc(NewsPost.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting news by category {category}: {str(e)}")
            return []
    
    def search_news_posts(self, search_term: str, limit: int = 20) -> List[NewsPost]:
        """Search news posts by title and content"""
        try:
            search_filter = or_(
                NewsPost.title.ilike(f"%{search_term}%"),
                NewsPost.content.ilike(f"%{search_term}%"),
                NewsPost.summary.ilike(f"%{search_term}%")
            )
            
            return self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user)
                )\
                .filter(
                    and_(
                        search_filter,
                        NewsPost.status == "PUBLISHED"
                    )
                )\
                .order_by(desc(NewsPost.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error searching news posts: {str(e)}")
            return []
    
    def get_related_news(self, news_id: int, category: str, limit: int = 5) -> List[NewsPost]:
        """Get related news posts based on category"""
        try:
            return self.db.query(NewsPost)\
                .options(
                    joinedload(NewsPost.author),
                    joinedload(NewsPost.business_user)
                )\
                .filter(
                    and_(
                        NewsPost.news_id != news_id,
                        NewsPost.category == category,
                        NewsPost.status == "PUBLISHED"
                    )
                )\
                .order_by(desc(NewsPost.added_on))\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting related news: {str(e)}")
            return []
    
    def get_news_analytics(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get news analytics for the specified number of days"""
        try:
            query = text("""
                SELECT 
                    np.news_id,
                    np.title,
                    np.view_count,
                    np.like_count,
                    np.share_count,
                    COUNT(nc.comment_id) as comment_count,
                    ROUND(
                        (np.like_count + np.share_count + COUNT(nc.comment_id)) * 100.0 / 
                        NULLIF(np.view_count, 0), 2
                    ) as engagement_rate,
                    np.added_on as created_date
                FROM news_posts np
                LEFT JOIN news_comments nc ON np.news_id = nc.news_id
                WHERE np.added_on >= DATE_SUB(NOW(), INTERVAL :days DAY)
                GROUP BY np.news_id, np.title, np.view_count, np.like_count, np.share_count, np.added_on
                ORDER BY engagement_rate DESC
            """)
            
            result = self.db.execute(query, {"days": days})
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"Error getting news analytics: {str(e)}")
            return []
    
    def _apply_filters(self, query, query_params: NewsPostQueryParams):
        """Apply filters to the query"""
        if query_params.category:
            query = query.filter(NewsPost.category == query_params.category)
        
        if query_params.status:
            query = query.filter(NewsPost.status == query_params.status)
        
        if query_params.author_id:
            query = query.filter(NewsPost.author_id == query_params.author_id)
        
        if query_params.business_user_id:
            query = query.filter(NewsPost.business_user_id == query_params.business_user_id)
        
        if query_params.is_featured is not None:
            query = query.filter(NewsPost.is_featured == query_params.is_featured)
        
        if query_params.is_top_story is not None:
            query = query.filter(NewsPost.is_top_story == query_params.is_top_story)
        
        if query_params.search:
            search_filter = or_(
                NewsPost.title.ilike(f"%{query_params.search}%"),
                NewsPost.content.ilike(f"%{query_params.search}%"),
                NewsPost.summary.ilike(f"%{query_params.search}%")
            )
            query = query.filter(search_filter)
        
        if query_params.tags:
            # Filter by tags (JSON array contains)
            for tag in query_params.tags:
                query = query.filter(NewsPost.tags.contains([tag]))
        
        return query
    
    def _apply_sorting(self, query, query_params: NewsPostQueryParams):
        """Apply sorting to the query"""
        sort_field = getattr(NewsPost, query_params.sort_by, NewsPost.added_on)
        if query_params.sort_order.lower() == "asc":
            query = query.order_by(asc(sort_field))
        else:
            query = query.order_by(desc(sort_field))
        return query
    
    def _apply_pagination(self, query, query_params: NewsPostQueryParams):
        """Apply pagination to the query"""
        offset = (query_params.page - 1) * query_params.page_size
        return query.offset(offset).limit(query_params.page_size)

    def get_all(self) -> List[NewsPost]:
        """Get all news posts"""
        try:
            return self.db.query(NewsPost).all()
        except Exception as e:
            logger.error(f"Error getting all news posts: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def get_by_id(self, news_id: int) -> Optional[NewsPost]:
        """Get news post by ID"""
        try:
            return self.db.query(NewsPost).filter(NewsPost.news_id == news_id).first()
        except Exception as e:
            logger.error(f"Error getting news post by ID {news_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def get_by_title(self, title: str) -> Optional[NewsPost]:
        """Get news post by title"""
        try:
            return self.db.query(NewsPost).filter(NewsPost.title == title).first()
        except Exception as e:
            logger.error(f"Error getting news post by title {title}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def create(self, news_post_data: NewsPostCreate, added_by: int) -> NewsPost:
        """Create a new news post"""
        try:
            news_post = NewsPost(
                title=news_post_data.title,
                content=news_post_data.content,
                summary=news_post_data.summary,
                author_id=news_post_data.author_id,
                business_user_id=news_post_data.business_user_id,
                category=news_post_data.category,
                tags=news_post_data.tags,
                featured_image=news_post_data.featured_image,
                status=news_post_data.status,
                publish_date=news_post_data.publish_date,
                expiry_date=news_post_data.expiry_date,
                is_featured=news_post_data.is_featured,
                is_top_story=news_post_data.is_top_story,
                seo_title=news_post_data.seo_title,
                seo_description=news_post_data.seo_description,
                seo_keywords=news_post_data.seo_keywords,
                meta_data=news_post_data.meta_data,
                added_by=added_by
            )
            self.db.add(news_post)
            self.db.commit()
            self.db.refresh(news_post)
            return news_post
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating news post: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create news post"
            )
    
    def update(self, news_id: int, update_data: NewsPostUpdate, modified_by: int) -> Optional[NewsPost]:
        """Update a news post"""
        try:
            news_post = self.get_by_id(news_id)
            if not news_post:
                return None
            
            # Update only provided fields - compatible with both Pydantic v1 and v2
            try:
                # Try Pydantic v2 method first
                update_dict = update_data.model_dump(exclude_unset=True)
            except AttributeError:
                # Fall back to Pydantic v1 method
                update_dict = update_data.dict(exclude_unset=True)
            for field, value in update_dict.items():
                if hasattr(news_post, field):
                    setattr(news_post, field, value)
            
            news_post.updated_by = modified_by
            self.db.commit()
            self.db.refresh(news_post)
            return news_post
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating news post {news_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update news post"
            )
    
    def delete(self, news_id: int, deleted_by: int) -> bool:
        """Delete a news post (soft delete)"""
        try:
            news_post = self.get_by_id(news_id)
            if not news_post:
                return False
            
            news_post.status = "DELETED"
            news_post.updated_by = deleted_by
            self.db.commit()
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting news post {news_id}: {str(e)}")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete news post"
            )

class NewsCommentRepository:
    """Repository for NewsComment operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_comment(self, comment_data: Dict[str, Any], user_id: int) -> NewsComment:
        """Create a new comment"""
        try:
            comment_data['added_by'] = user_id
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
    
    def get_comments_by_news_id(self, news_id: int) -> List[NewsComment]:
        """Get all comments for a news post with user information"""
        try:
            return self.db.query(NewsComment)\
                .options(
                    joinedload(NewsComment.user),
                    joinedload(NewsComment.added_by_user),
                    joinedload(NewsComment.updated_by_user)
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

class NewsLikeRepository:
    """Repository for NewsLike operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_like(self, like_data: Dict[str, Any]) -> NewsLike:
        """Create a new like"""
        try:
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
    
    def get_likes_by_news_id(self, news_id: int) -> List[NewsLike]:
        """Get all likes for a news post"""
        try:
            return self.db.query(NewsLike)\
                .options(joinedload(NewsLike.user))\
                .filter(NewsLike.news_id == news_id)\
                .all()
        except Exception as e:
            logger.error(f"Error getting likes for news {news_id}: {str(e)}")
            return []
    
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

class NewsShareRepository:
    """Repository for NewsShare operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
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
    
    def get_shares_by_news_id(self, news_id: int) -> List[NewsShare]:
        """Get all shares for a news post"""
        try:
            return self.db.query(NewsShare)\
                .options(joinedload(NewsShare.user))\
                .filter(NewsShare.news_id == news_id)\
                .all()
        except Exception as e:
            logger.error(f"Error getting shares for news {news_id}: {str(e)}")
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
