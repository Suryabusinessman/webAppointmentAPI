from fastapi import HTTPException, status
from app.repositories.UserModules.usertypes import UserTypeRepository
from app.schemas.UserModules.usertypes import UserTypeCreate, UserTypeUpdate


class UserTypeService:
    def __init__(self, user_type_repository: UserTypeRepository, security_key: str):
        self.user_type_repository = user_type_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_user_types(self, security_key: str):
        """Fetch all user types."""
        self.validate_security_key(security_key)
        user_types = self.user_type_repository.get_all()
        return {
            "status": "success",
            "message": "User types retrieved successfully.",
            "data": user_types
        }

    def get_user_type_by_id(self, user_type_id: int, security_key: str):
        """Fetch a user type by its ID."""
        self.validate_security_key(security_key)
        user_type = self.user_type_repository.get_by_id(user_type_id)
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )
        return {
            "status": "success",
            "message": f"User type with ID {user_type_id} retrieved successfully.",
            "data": user_type
        }

    def create_user_type(self, user_type_data: UserTypeCreate, security_key: str, added_by: int):
        """Create a new user type."""
        self.validate_security_key(security_key)

        # Check if a user type with the same name already exists
        existing_user_type = self.user_type_repository.get_by_name(user_type_data.User_Type_Name)
        if existing_user_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User type with name '{user_type_data.User_Type_Name}' already exists."
            )

        # Create the new user type
        new_user_type = self.user_type_repository.create(user_type_data, added_by)
        return {
            "status": "success",
            "color":"success",
            "message": "User type created successfully.",
            "data": new_user_type
        }

    def update_user_type(self, user_type_id: int, user_type_data: UserTypeUpdate, security_key: str, modified_by: int):
        """Update an existing user type."""
        self.validate_security_key(security_key)

        # Ensure the user type exists
        user_type = self.user_type_repository.get_by_id(user_type_id)
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )

        # Prevent updating to a duplicate name
        if user_type_data.User_Type_Name:
            existing_user_type = self.user_type_repository.get_by_name(user_type_data.User_Type_Name)
            if existing_user_type and existing_user_type.User_Type_Id != user_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Another user type with name '{user_type_data.User_Type_Name}' already exists."
                )

        # Update the user type
        updated_user_type = self.user_type_repository.update(user_type_id, user_type_data, modified_by)
        return {
            "status": "success",
            "color":"success",
            "message": f"User type with ID {user_type_data.User_Type_Name} updated successfully.",
            "data": updated_user_type
        }

    def delete_user_type(self, user_type_id: int, security_key: str, deleted_by: int):
        """Delete a user type by its ID."""
        self.validate_security_key(security_key)

        # Ensure the user type exists
        user_type = self.user_type_repository.get_by_id(user_type_id)
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )

        # Perform the deletion
        result = self.user_type_repository.delete(user_type_id, deleted_by)
        return {
            "status": "success",
            "color":"success",
            "message": f"User type with ID {user_type_id} deleted successfully.",
            "data": result
        }