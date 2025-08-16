from typing import List, Optional, Dict, Any, TypeVar, Generic, Union
from sqlalchemy.orm import Session, Query
from sqlalchemy import and_, or_, desc, asc
from fastapi import HTTPException, status
from pydantic import BaseModel
from datetime import datetime
import logging
from app.schemas.common import QueryParams, APIResponse, SuccessResponse, ErrorResponse
from app.core.security import SecurityManager

logger = logging.getLogger(__name__)

# Generic types
T = TypeVar('T')  # SQLAlchemy model type
CreateSchema = TypeVar('CreateSchema', bound=BaseModel)
UpdateSchema = TypeVar('UpdateSchema', bound=BaseModel)
ResponseSchema = TypeVar('ResponseSchema', bound=BaseModel)

class BaseService(Generic[T, CreateSchema, UpdateSchema, ResponseSchema]):
    """Base service class providing common CRUD operations"""
    
    def __init__(self, db: Session, model: T):
        self.db = db
        self.model = model
    
    def get_by_id(self, id: int) -> Optional[T]:
        """Get a record by ID"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first()
        except Exception as e:
            logger.error(f"Error getting record by ID {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def get_all(self, query_params: QueryParams = None) -> List[T]:
        """Get all records with optional filtering and pagination"""
        try:
            query = self.db.query(self.model)
            
            if query_params:
                query = self._apply_filters(query, query_params)
                query = self._apply_pagination(query, query_params)
                query = self._apply_sorting(query, query_params)
            
            return query.all()
        except Exception as e:
            logger.error(f"Error getting all records: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def create(self, data: CreateSchema, user_id: int = None) -> T:
        """Create a new record"""
        try:
            # Convert Pydantic model to dict
            if hasattr(data, 'dict'):
                db_data = data.dict()
            else:
                db_data = data
            
            # Add audit fields
            if user_id:
                db_data['added_by'] = user_id
            db_data['added_on'] = datetime.utcnow()
            
            # Create model instance
            db_obj = self.model(**db_data)
            self.db.add(db_obj)
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Created {self.model.__name__} with ID: {db_obj.id}")
            return db_obj
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating record: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create record"
            )
    
    def update(self, id: int, data: UpdateSchema, user_id: int = None) -> T:
        """Update an existing record"""
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} not found"
                )
            
            # Convert Pydantic model to dict
            if hasattr(data, 'dict'):
                update_data = data.dict(exclude_unset=True)
            else:
                update_data = data
            
            # Add audit fields
            if user_id:
                update_data['modified_by'] = user_id
            update_data['modified_on'] = datetime.utcnow()
            
            # Update fields
            for field, value in update_data.items():
                if hasattr(db_obj, field):
                    setattr(db_obj, field, value)
            
            self.db.commit()
            self.db.refresh(db_obj)
            
            logger.info(f"Updated {self.model.__name__} with ID: {id}")
            return db_obj
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating record {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update record"
            )
    
    def delete(self, id: int, user_id: int = None, soft_delete: bool = True) -> bool:
        """Delete a record (soft or hard delete)"""
        try:
            db_obj = self.get_by_id(id)
            if not db_obj:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"{self.model.__name__} not found"
                )
            
            if soft_delete and hasattr(db_obj, 'is_deleted'):
                # Soft delete
                db_obj.is_deleted = 'Y'
                if user_id:
                    db_obj.deleted_by = user_id
                db_obj.deleted_on = datetime.utcnow()
                self.db.commit()
                logger.info(f"Soft deleted {self.model.__name__} with ID: {id}")
            else:
                # Hard delete
                self.db.delete(db_obj)
                self.db.commit()
                logger.info(f"Hard deleted {self.model.__name__} with ID: {id}")
            
            return True
            
        except HTTPException:
            raise
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting record {id}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete record"
            )
    
    def bulk_create(self, data_list: List[CreateSchema], user_id: int = None) -> List[T]:
        """Create multiple records"""
        try:
            created_objects = []
            for data in data_list:
                db_obj = self.create(data, user_id)
                created_objects.append(db_obj)
            
            logger.info(f"Bulk created {len(created_objects)} {self.model.__name__} records")
            return created_objects
            
        except Exception as e:
            logger.error(f"Error in bulk create: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create records"
            )
    
    def count(self, query_params: QueryParams = None) -> int:
        """Count records with optional filtering"""
        try:
            query = self.db.query(self.model)
            
            if query_params:
                query = self._apply_filters(query, query_params)
            
            return query.count()
        except Exception as e:
            logger.error(f"Error counting records: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred"
            )
    
    def exists(self, id: int) -> bool:
        """Check if a record exists"""
        try:
            return self.db.query(self.model).filter(self.model.id == id).first() is not None
        except Exception as e:
            logger.error(f"Error checking existence: {str(e)}")
            return False
    
    def _apply_filters(self, query: Query, query_params: QueryParams) -> Query:
        """Apply filters to query"""
        if query_params.search and hasattr(self.model, 'name'):
            search_term = f"%{query_params.search}%"
            query = query.filter(self.model.name.ilike(search_term))
        
        if query_params.filters:
            for field, value in query_params.filters.items():
                if hasattr(self.model, field):
                    query = query.filter(getattr(self.model, field) == value)
        
        if query_params.date_from and hasattr(self.model, 'created_at'):
            query = query.filter(self.model.created_at >= query_params.date_from)
        
        if query_params.date_to and hasattr(self.model, 'created_at'):
            query = query.filter(self.model.created_at <= query_params.date_to)
        
        # Always filter out soft deleted records
        if hasattr(self.model, 'is_deleted'):
            query = query.filter(self.model.is_deleted == 'N')
        
        return query
    
    def _apply_pagination(self, query: Query, query_params: QueryParams) -> Query:
        """Apply pagination to query"""
        offset = (query_params.page - 1) * query_params.page_size
        return query.offset(offset).limit(query_params.page_size)
    
    def _apply_sorting(self, query: Query, query_params: QueryParams) -> Query:
        """Apply sorting to query"""
        if query_params.sort_by and hasattr(self.model, query_params.sort_by):
            sort_field = getattr(self.model, query_params.sort_by)
            if query_params.sort_order == 'desc':
                return query.order_by(desc(sort_field))
            else:
                return query.order_by(asc(sort_field))
        return query
    
    def create_response(self, success: bool, message: str, data: Any = None, errors: List[str] = None) -> APIResponse:
        """Create standardized API response"""
        return APIResponse(
            success=success,
            message=message,
            data=data,
            errors=errors,
            timestamp=datetime.utcnow()
        )
    
    def success_response(self, message: str, data: Any = None) -> APIResponse:
        """Create success response"""
        return self.create_response(True, message, data)
    
    def error_response(self, message: str, errors: List[str] = None) -> APIResponse:
        """Create error response"""
        return self.create_response(False, message, errors=errors)

class AuditService:
    """Service for audit logging"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def log_action(self, action_type: str, table_name: str, record_id: int, 
                   user_id: int = None, old_values: Dict[str, Any] = None, 
                   new_values: Dict[str, Any] = None, session_id: str = None,
                   ip_address: str = None, user_agent: str = None):
        """Log an audit action"""
        try:
            from app.models.common import AuditLog
            
            audit_log = AuditLog(
                action_type=action_type,
                table_name=table_name,
                record_id=record_id,
                user_id=user_id,
                old_values=old_values,
                new_values=new_values,
                session_id=session_id,
                ip_address=ip_address,
                user_agent=user_agent,
                created_at=datetime.utcnow()
            )
            
            self.db.add(audit_log)
            self.db.commit()
            
            logger.info(f"Audit log created: {action_type} on {table_name} record {record_id}")
            
        except Exception as e:
            logger.error(f"Error creating audit log: {str(e)}")
            # Don't raise exception for audit logging failures

class NotificationService:
    """Service for notifications"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(self, notification_type: str, title: str, message: str,
                          recipient_id: int, sender_id: int = None, priority: str = "normal",
                          action_data: Dict[str, Any] = None):
        """Create a new notification"""
        try:
            from app.models.common import Notification
            
            notification = Notification(
                notification_type=notification_type,
                title=title,
                message=message,
                recipient_id=recipient_id,
                sender_id=sender_id,
                priority=priority,
                action_data=action_data,
                is_read='N',
                created_at=datetime.utcnow()
            )
            
            self.db.add(notification)
            self.db.commit()
            self.db.refresh(notification)
            
            logger.info(f"Notification created for user {recipient_id}: {title}")
            return notification
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating notification: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create notification"
            )
    
    def mark_as_read(self, notification_id: int, user_id: int):
        """Mark notification as read"""
        try:
            from app.models.common import Notification
            
            notification = self.db.query(Notification).filter(
                Notification.notification_id == notification_id,
                Notification.recipient_id == user_id
            ).first()
            
            if not notification:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Notification not found"
                )
            
            notification.is_read = 'Y'
            notification.updated_at = datetime.utcnow()
            self.db.commit()
            
            logger.info(f"Notification {notification_id} marked as read by user {user_id}")
            return notification
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to mark notification as read"
            ) 