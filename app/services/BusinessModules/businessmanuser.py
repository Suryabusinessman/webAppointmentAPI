from fastapi import HTTPException, status
from typing import List
from app.repositories.BusinessModules.businessmanuser import BusinessmanUserRepository
from app.schemas.BusinessModules.businessmanuser import BusinessmanUserCreate, BusinessmanUserUpdate


class BusinessmanUserService:
    def __init__(self, businessman_user_repository: BusinessmanUserRepository, security_key: str):
        self.businessman_user_repository = businessman_user_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_businessman_users(self, security_key: str):
        """Fetch all user types."""
        self.validate_security_key(security_key)
        businessman_user = self.businessman_user_repository.get_all()
        return {
            "status": "success",
            "message": "User types retrieved successfully.",
            "data": businessman_user
        }
    def get_businessman_user_by_id(self, businessman_user_id: int, security_key: str):
        """Fetch a businessman user by its ID."""
        self.validate_security_key(security_key)
        businessman_user = self.businessman_user_repository.get_by_id(businessman_user_id)
        if not businessman_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Businessman User with ID {businessman_user_id} not found."
            )
        return {
            "status": "success",
            "message": f"Businessman User with ID {businessman_user_id} retrieved successfully.",
            "data": businessman_user
        }
    def create_businessman_user(self, businessman_user_data: BusinessmanUserCreate, security_key: str, added_by: int):
        """Create a new businessman user."""
        self.validate_security_key(security_key)

        # Check if a businessman user with the same name already exists
        existing_businessman_user = self.businessman_user_repository.get_by_user_and_bussienss_type(
            bussienss_type_id=businessman_user_data.Business_Type_Id,
            user_id=businessman_user_data.User_Id,
            user_type_id=businessman_user_data.User_Type_Id
        )
        if existing_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Businessman User with name already exists."
            )

        # Create the new businessman user
        new_businessman_user = self.businessman_user_repository.create(businessman_user_data, added_by)
        if not new_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Businessman User."
            )
        # Return the newly created businessman user object

        return {
            "status": "success",
            "message": "Businessman User created successfully.",
            "data": new_businessman_user
        }
    def create_multiple_businessman_users(
        self,
        users_data: List[BusinessmanUserCreate],
        security_key: str,
        added_by: int
        ):
        results = {
            "success": [],
            "failed": []
        }

        for index, data in enumerate(users_data):
            try:
                # Basic field-level validation
                if not data.Business_Type_Id or not data.Business_Type_Name:
                    results["failed"].append({
                        "index": index,
                        "reason": "Missing Business_Type_Id or Business_Type_Name"
                    })
                    continue

                # Insert record
                user = self.create_businessman_user(data, security_key, added_by)
                if user and user.get("data"):
                    results["success"].append(user["data"])
                else:
                    results["failed"].append({
                        "index": index,
                        "reason": "Insertion failed with no data returned"
                    })

            except Exception as e:
                # Log the exception for each failed item
                results["failed"].append({
                    "index": index,
                    "reason": str(e)
                })

        return results
    def update_businessman_user(self, businessman_user_id: int, businessman_user_data: BusinessmanUserUpdate, security_key: str, updated_by: int):
        """Update an existing businessman user."""
        self.validate_security_key(security_key)

        # Fetch the existing businessman user
        existing_businessman_user = self.businessman_user_repository.get_by_id(businessman_user_id)
        if not existing_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Businessman User with ID {businessman_user_id} not found."
            )
        existing_businessman_user_check = self.businessman_user_repository.get_by_user_and_bussienss_type(
            bussienss_type_id=businessman_user_data.Business_Type_Id,
            user_id=businessman_user_data.User_Id,
            user_type_id=businessman_user_data.User_Type_Id
        )
        if existing_businessman_user_check and existing_businessman_user_check.Businessman_User_Id != businessman_user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Businessman User with this name already exists."
            )
        # Update the businessman user details
        updated_businessman_user = self.businessman_user_repository.update(businessman_user_id, businessman_user_data, updated_by)
        if not updated_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update BusinessMan User."
            )
        return {
            "status": "success",
            "message": "BusinessMan User updated successfully.",
            "data": updated_businessman_user
        }
    def delete_businessman_user(self, businessman_user_id: int, security_key: str, deleted_by: int):

        """Delete a Business Man User by its ID."""
        self.validate_security_key(security_key)

        # Ensure the Business Man User exists
        businessman_user = self.businessman_user_repository.get_by_id(businessman_user_id)
        if not businessman_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Man User Permission with ID {businessman_user_id} not found."
            )

        # Perform the deletion
        result = self.businessman_user_repository.delete(businessman_user_id, deleted_by)
        return {
            "status": "success",
            "message": f"Business Man User with ID {businessman_user_id} deleted successfully.",
            "data": result
        }

