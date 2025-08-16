from fastapi import HTTPException, status
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.schemas.UserModules.userpermissions import UserPermissionCreate, UserPermissionUpdate, UserPermissionResponse


class UserPermissionService:
    def __init__(self, user_permission_repository: UserPermissionRepository, security_key: str):
        self.user_permission_repository = user_permission_repository
        self.security_key = security_key

    def get_all_user_permissions(self, security_key: str):
        """Fetch all User permissions."""
        user_permissions = self.user_permission_repository.get_all()
        return {
            "status": "success",
            "message": "User permissions retrieved successfully.",
            "data": user_permissions
        }

    def get_user_permission_by_id(self, user_permission_id: int, security_key: str):
        """Fetch a User Permission by its ID."""
        user_permission = self.user_permission_repository.get_by_id(user_permission_id)
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )
        return {
            "status": "success",
            "message": f"User Permission with ID {user_permission_id} retrieved successfully.",
            "data": user_permission
        }

    def get_by_user_type(self, user_type_id: int, security_key: str):
        """Fetch all User Permissions for a given User Type ID."""
        user_permissions = self.user_permission_repository.get_by_user_type(user_type_id)
        return {
            "status": "success",
            "message": f"User permissions for user type {user_type_id} retrieved successfully.",
            "data": user_permissions
        }

    def get_user_permissions_with_pages(self, user_type_id: int, security_key: str):
        """Fetch all User Permissions with their corresponding Page names for a given User Type ID."""
        permissions = self.user_permission_repository.get_user_permissions_with_pages(user_type_id)
        return {
            "status": "success",
            "message": f"User permissions with pages for user type {user_type_id} retrieved successfully.",
            "data": permissions
        }

    def create_user_permission(self, user_permission_data: UserPermissionCreate, security_key: str, added_by: int):
        """Create a new user permission."""
        # Check if a permission for this page_id and user_type_id already exists
        existing_permission = self.user_permission_repository.get_by_page_and_user_type(
            page_id=user_permission_data.page_id,
            user_type_id=user_permission_data.user_type_id
        )

        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User permission with this Page ID and User Type ID already exists."
            )

        # Create the new user permission
        new_user_permission = self.user_permission_repository.create(user_permission_data, added_by)
        return {
            "status": "success",
            "message": "User permission created successfully.",
            "data": new_user_permission
        }

    def update_user_permission(self, user_permission_id: int, user_permission_data: UserPermissionUpdate, security_key: str, modified_by: int):
        """Update an existing user permission."""
        # Ensure the user permission exists
        user_permission = self.user_permission_repository.get_by_id(user_permission_id)
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User permission with ID {user_permission_id} not found."
            )

        # Check if the updated page_id and user_type_id combo would conflict
        new_page_id = user_permission_data.page_id if user_permission_data.page_id is not None else user_permission.page_id
        new_user_type_id = user_permission_data.user_type_id if user_permission_data.user_type_id is not None else user_permission.user_type_id

        existing_permission = self.user_permission_repository.get_by_page_and_user_type(
            page_id=new_page_id,
            user_type_id=new_user_type_id
        )

        if existing_permission and existing_permission.user_permission_id != user_permission_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Another user permission with this Page ID and User Type ID already exists."
            )

        # Perform the update
        updated_user_permission = self.user_permission_repository.update(user_permission_id, user_permission_data, modified_by)
        return {
            "status": "success",
            "message": f"User permission with ID {user_permission_id} updated successfully.",
            "data": updated_user_permission
        }

    def delete_user_permission(self, user_permission_id: int, security_key: str, deleted_by: int):
        """Delete a User Permission by its ID."""
        # Ensure the User Permission exists
        user_permission = self.user_permission_repository.get_by_id(user_permission_id)
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )

        # Perform the deletion
        result = self.user_permission_repository.delete(user_permission_id, deleted_by)
        return {
            "status": "success",
            "message": f"User Permission with ID {user_permission_id} deleted successfully.",
            "data": result
        }

    def activate_user_permission(self, user_permission_id: int, security_key: str, modified_by: int):
        """Activate a user permission."""
        activated_permission = self.user_permission_repository.activate_permission(user_permission_id, modified_by)
        return {
            "status": "success",
            "message": f"User permission with ID {user_permission_id} activated successfully.",
            "data": activated_permission
        }

    def deactivate_user_permission(self, user_permission_id: int, security_key: str, modified_by: int):
        """Deactivate a user permission."""
        deactivated_permission = self.user_permission_repository.deactivate_permission(user_permission_id, modified_by)
        return {
            "status": "success",
            "message": f"User permission with ID {user_permission_id} deactivated successfully.",
            "data": deactivated_permission
        }

    def get_active_user_permissions(self, security_key: str):
        """Get all active user permissions."""
        permissions = self.user_permission_repository.get_active_permissions()
        return {
            "status": "success",
            "message": "Active user permissions retrieved successfully.",
            "data": permissions
        }

    def get_inactive_user_permissions(self, security_key: str):
        """Get all inactive user permissions."""
        permissions = self.user_permission_repository.get_inactive_permissions()
        return {
            "status": "success",
            "message": "Inactive user permissions retrieved successfully.",
            "data": permissions
        }