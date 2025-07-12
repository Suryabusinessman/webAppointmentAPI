from fastapi import HTTPException, status
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.schemas.UserModules.userpermissions import UserPermissionCreate, UserPermissionUpdate


class UserPermissionService:
    def __init__(self, user_permission_repository: UserPermissionRepository, security_key: str):
        self.user_permission_repository = user_permission_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_user_permission(self, security_key: str):
        """Fetch all User permission."""
        self.validate_security_key(security_key)
        user_permission = self.user_permission_repository.get_all()
        return {
            "status": "success",
            "message": "User permission retrieved successfully.",
            "data": user_permission
        }

    def get_user_permission_by_id(self, user_permission_id: int, security_key: str):
        """Fetch a User Permission by its ID."""
        self.validate_security_key(security_key)
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

    def create_user_permission(self, user_permission_data: UserPermissionCreate, security_key: str, added_by: int):
        """Create a new user permission."""
        self.validate_security_key(security_key)

        # Check if a permission for this Page ID and User Type ID already exists
        existing_permission = self.user_permission_repository.get_by_page_and_user_type(
            page_id=user_permission_data.Page_Id,
            user_type_id=user_permission_data.User_Type_Id
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
        self.validate_security_key(security_key)

        # Ensure the user permission exists
        user_permission = self.user_permission_repository.get_by_id(user_permission_id)
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User permission with ID {user_permission_id} not found."
            )

        # Check if the updated Page ID and User Type ID combo would conflict
        new_page_id = user_permission_data.Page_Id if user_permission_data.Page_Id is not None else user_permission.Page_Id
        new_user_type_id = user_permission_data.User_Type_Id if user_permission_data.User_Type_Id is not None else user_permission.User_Type_Id

        existing_permission = self.user_permission_repository.get_by_page_and_user_type(
            page_id=new_page_id,
            user_type_id=new_user_type_id
        )

        if existing_permission and existing_permission.User_Permission_Id != user_permission_id:
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
        self.validate_security_key(security_key)

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