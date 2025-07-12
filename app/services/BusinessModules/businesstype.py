from fastapi import HTTPException, status
from app.repositories.BusinessModules.businesstype import BusinessTypeRepository
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate



class BusinessTypeService:
    def __init__(self, business_type_repository: BusinessTypeRepository, security_key: str):
        self.business_type_repository = business_type_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_business_types(self, security_key: str):
        """Fetch all user types."""
        self.validate_security_key(security_key)
        business_type = self.business_type_repository.get_all()
        return {
            "status": "success",
            "message": "User types retrieved successfully.",
            "data": business_type
        }

    def get_business_type_by_id(self, business_type_id: int, security_key: str):
        """Fetch a business type by its ID."""
        self.validate_security_key(security_key)
        business_type = self.business_type_repository.get_by_id(business_type_id)
        if not business_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Type with ID {business_type_id} not found."
            )
        return {
            "status": "success",
            "message": f"Business Type with ID {business_type_id} retrieved successfully.",
            "data": business_type
        }

    def create_business_type(self, business_type_data: BusinessTypeCreate, security_key: str, added_by: int):
        """Create a new business type."""
        self.validate_security_key(security_key)

        # Check if a business type with the same name already exists
        existing_business_type = self.business_type_repository.get_by_name(business_type_data.Business_Type_Name)
        if existing_business_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business Type with name '{business_type_data.Business_Type_Name}' already exists."
            )

        # Create the new business type
        new_business_type = self.business_type_repository.create(business_type_data, added_by)
        if not new_business_type:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Business Type."
            )
        return {
            "status": "success",
            "message": "Business Type created successfully.",
            "data": new_business_type
        }

    def update_business_type(self, business_type_id: int, business_type_data: BusinessTypeUpdate, security_key: str, modified_by: int):
        """Update an existing business type."""
        self.validate_security_key(security_key)

        # Ensure the business type exists
        business_type = self.business_type_repository.get_by_id(business_type_id)
        if not business_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Type with ID {business_type_id} not found."
            )

        # Prevent updating to a duplicate name
        if business_type_data.Business_Type_Name:
            existing_business_type = self.business_type_repository.get_by_name(business_type_data.Business_Type_Name)
            if existing_business_type and existing_business_type.Business_Type_Id != business_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Another business type with name '{business_type_data.Business_Type_Name}' already exists."
                )

        # Update the business type
        updated_business_type = self.business_type_repository.update(business_type_id, business_type_data, modified_by)
        if not updated_business_type:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update Business Type."
            )
        return {
            "status": "success",
            "message": f"Business Type with ID {business_type_id} updated successfully.",
            "data": updated_business_type
        }

    def delete_business_type(self, business_type_id: int, security_key: str, deleted_by: int):
        """Delete a business type by its ID."""
        self.validate_security_key(security_key)

        # Ensure the business type exists
        business_type = self.business_type_repository.get_by_id(business_type_id)
        if not business_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Type with ID {business_type_id} not found."
            )

        # Perform the deletion
        result = self.business_type_repository.delete(business_type_id, deleted_by)
        return {
            "status": "success",
            "color":"success",
            "message": f"Business Type with ID {business_type_id} deleted successfully.",
            "data": result
        }