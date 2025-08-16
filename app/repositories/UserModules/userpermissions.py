from sqlalchemy.orm import Session
from app.models.UserModules.userpermissions import UserPermission
from app.models.UserModules.pages import Page
from app.models.UserModules.usertypes import UserType
from app.schemas.UserModules.userpermissions import UserPermissionCreate, UserPermissionUpdate, UserPermissionResponse
from fastapi import HTTPException, status
from datetime import datetime


class UserPermissionRepository:
    """Repository for user permissions."""
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active user permissions with page names and user type names."""
        user_permissions = self.db.query(UserPermission, Page, UserType).join(
            Page, UserPermission.page_id == Page.page_id
        ).join(
            UserType, UserPermission.user_type_id == UserType.user_type_id
        ).filter(
            UserPermission.is_deleted == 'N',
            Page.is_deleted == 'N',
            UserType.is_active == 'Y'
        ).all()
        
        if not user_permissions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user permissions found in the database."
            )
        
        result = []
        for permission, page, user_type in user_permissions:
            result.append({
                "user_permission_id": permission.user_permission_id,
                "user_type_id": permission.user_type_id,
                "user_type_name": user_type.type_name,
                "page_id": page.page_id,
                "page_name": page.page_name,
                "page_display_text": page.page_display_text,
                "page_navigation_url": page.page_navigation_url,
                "page_parent_id": page.page_parent_id,
                "is_internal": page.is_internal,
                "can_view": permission.can_view,
                "can_create": permission.can_create,
                "can_update": permission.can_update,
                "can_delete": permission.can_delete,
                "added_by": permission.added_by,
                "modified_by": permission.modified_by,
                "is_deleted": permission.is_deleted,
                "deleted_on": permission.deleted_on.isoformat() if permission.deleted_on else None,
                "added_on": permission.added_on.isoformat() if permission.added_on else None,
                "modified_on": permission.modified_on.isoformat() if permission.modified_on else None,
                "deleted_by": permission.deleted_by
            })
        
        return result

    def get_by_id(self, user_permission_id: int):
        """Fetch a User Permission by its ID with page and user type names."""
        user_permission = self.db.query(UserPermission, Page, UserType).join(
            Page, UserPermission.page_id == Page.page_id
        ).join(
            UserType, UserPermission.user_type_id == UserType.user_type_id
        ).filter(
            UserPermission.user_permission_id == user_permission_id,
            UserPermission.is_deleted == 'N',
            Page.is_deleted == 'N',
            UserType.is_active == 'Y'
        ).first()
        
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )
        
        permission, page, user_type = user_permission
        return {
            "user_permission_id": permission.user_permission_id,
            "user_type_id": permission.user_type_id,
            "user_type_name": user_type.type_name,
            "page_id": page.page_id,
            "page_name": page.page_name,
            "page_display_text": page.page_display_text,
            "page_navigation_url": page.page_navigation_url,
            "page_parent_id": page.page_parent_id,
            "is_internal": page.is_internal,
            "can_view": permission.can_view,
            "can_create": permission.can_create,
            "can_update": permission.can_update,
            "can_delete": permission.can_delete,
            "added_by": permission.added_by,
            "modified_by": permission.modified_by,
            "is_deleted": permission.is_deleted,
            "deleted_on": permission.deleted_on.isoformat() if permission.deleted_on else None,
            "added_on": permission.added_on.isoformat() if permission.added_on else None,
            "modified_on": permission.modified_on.isoformat() if permission.modified_on else None,
            "deleted_by": permission.deleted_by
        }

    def get_by_page_and_user_type(self, page_id: int, user_type_id: int):
        """Check if a user permission exists for a given Page ID and User Type ID."""
        return self.db.query(UserPermission).filter(
            UserPermission.page_id == page_id,
            UserPermission.user_type_id == user_type_id,
            UserPermission.is_deleted == 'N'
        ).first()

    def get_by_user_type(self, user_type_id: int):
        """Fetch all User Permissions for a given User Type ID with page names."""
        user_permissions = self.db.query(UserPermission, Page).join(
            Page, UserPermission.page_id == Page.page_id
        ).filter(
            UserPermission.user_type_id == user_type_id,
            UserPermission.is_deleted == 'N',
            Page.is_deleted == 'N'
        ).all()
        
        result = []
        for permission, page in user_permissions:
            result.append({
                "user_permission_id": permission.user_permission_id,
                "user_type_id": permission.user_type_id,
                "page_id": page.page_id,
                "page_name": page.page_name,
                "page_display_text": page.page_display_text,
                "page_navigation_url": page.page_navigation_url,
                "page_parent_id": page.page_parent_id,
                "is_internal": page.is_internal,
                "can_view": permission.can_view,
                "can_create": permission.can_create,
                "can_update": permission.can_update,
                "can_delete": permission.can_delete,
                "added_by": permission.added_by,
                "modified_by": permission.modified_by,
                "is_deleted": permission.is_deleted,
                "deleted_on": permission.deleted_on.isoformat() if permission.deleted_on else None,
                "added_on": permission.added_on.isoformat() if permission.added_on else None,
                "modified_on": permission.modified_on.isoformat() if permission.modified_on else None,
                "deleted_by": permission.deleted_by
            })
        
        return result

    def get_user_permissions_with_pages(self, user_type_id: int):
        """Fetch all User Permissions with their corresponding Page names for a given User Type ID."""
        permissions = self.db.query(UserPermission, Page).join(
            Page, UserPermission.page_id == Page.page_id
        ).filter(
            UserPermission.user_type_id == user_type_id,
            UserPermission.is_deleted == 'N',
            Page.is_deleted == 'N'
        ).all()

        result = []
        for permission, page in permissions:
            result.append({
                "user_permission_id": permission.user_permission_id,
                "user_type_id": permission.user_type_id,
                "page_id": page.page_id,
                "page_name": page.page_name,
                "page_display_text": page.page_display_text,
                "page_navigation_url": page.page_navigation_url,
                "page_parent_id": page.page_parent_id,
                "is_internal": page.is_internal,
                "can_view": permission.can_view,
                "can_create": permission.can_create,
                "can_update": permission.can_update,
                "can_delete": permission.can_delete,
            })

        return result

    def create(self, user_permission_data: UserPermissionCreate, added_by: int):
        """Create a new User Permission."""
        # Check if a UserPermission with the same page_id and user_type_id already exists
        existing_permission = self.db.query(UserPermission).filter(
            UserPermission.page_id == user_permission_data.page_id,
            UserPermission.user_type_id == user_permission_data.user_type_id,
            UserPermission.is_deleted == 'N'
        ).first()

        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A User Permission with this Page ID and User Type ID already exists."
            )

        new_user_permission = UserPermission(
            user_type_id=user_permission_data.user_type_id,
            page_id=user_permission_data.page_id,
            can_view=user_permission_data.can_view,
            can_create=user_permission_data.can_create,
            can_update=user_permission_data.can_update,
            can_delete=user_permission_data.can_delete,
            added_by=added_by,
            added_on=datetime.utcnow(),
            modified_by=added_by,
            modified_on=datetime.utcnow(),
            is_deleted='N'
        )

        self.db.add(new_user_permission)
        self.db.commit()
        self.db.refresh(new_user_permission)
        return new_user_permission

    def update(self, user_permission_id: int, user_permission_data: UserPermissionUpdate, modified_by: int):
        """Update an existing User Permission."""
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.user_permission_id == user_permission_id,
            UserPermission.is_deleted == 'N'
        ).first()

        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )

        # Update fields if provided
        if user_permission_data.user_type_id is not None:
            user_permission.user_type_id = user_permission_data.user_type_id
        if user_permission_data.page_id is not None:
            user_permission.page_id = user_permission_data.page_id
        if user_permission_data.can_view is not None:
            user_permission.can_view = user_permission_data.can_view
        if user_permission_data.can_create is not None:
            user_permission.can_create = user_permission_data.can_create
        if user_permission_data.can_update is not None:
            user_permission.can_update = user_permission_data.can_update
        if user_permission_data.can_delete is not None:
            user_permission.can_delete = user_permission_data.can_delete

        user_permission.modified_by = modified_by
        user_permission.modified_on = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user_permission)
        return user_permission

    def delete(self, user_permission_id: int, deleted_by: int):
        """Soft delete a User Permission."""
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.user_permission_id == user_permission_id,
            UserPermission.is_deleted == 'N'
        ).first()

        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )

        user_permission.is_deleted = 'Y'
        user_permission.deleted_by = deleted_by
        user_permission.deleted_on = datetime.utcnow()

        self.db.commit()
        return user_permission

    def get_active_permissions(self):
        """Fetch all active user permissions."""
        return self.db.query(UserPermission).filter(
            UserPermission.is_deleted == 'N'
        ).all()

    def get_inactive_permissions(self):
        """Fetch all inactive user permissions."""
        return self.db.query(UserPermission).filter(
            UserPermission.is_deleted == 'Y'
        ).all()

    def activate_permission(self, user_permission_id: int, modified_by: int):
        """Activate a user permission."""
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.user_permission_id == user_permission_id
        ).first()

        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )

        user_permission.is_deleted = 'N'
        user_permission.modified_by = modified_by
        user_permission.modified_on = datetime.utcnow()

        self.db.commit()
        return user_permission

    def deactivate_permission(self, user_permission_id: int, modified_by: int):
        """Deactivate a user permission."""
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.user_permission_id == user_permission_id,
            UserPermission.is_deleted == 'N'
        ).first()

        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )

        user_permission.is_deleted = 'Y'
        user_permission.modified_by = modified_by
        user_permission.modified_on = datetime.utcnow()

        self.db.commit()
        return user_permission