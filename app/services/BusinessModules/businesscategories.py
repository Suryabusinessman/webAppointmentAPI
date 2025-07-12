from fastapi import HTTPException, status
from app.repositories.BusinessModules.businesscategories import BusinessCategoryRepository
from app.schemas.BusinessModules.businesscategories import BusinessCategoryCreate, BusinessCategoryUpdate

class BusinessCategoryService:
    def __init__(self, business_category_repository: BusinessCategoryRepository, security_key: str):
        self.business_category_repository = business_category_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_business_categories(self, security_key: str):
        """Fetch all user types."""
        self.validate_security_key(security_key)
        business_category = self.business_category_repository.get_all()
        return {
            "status": "success",
            "message": "Business Categories retrieved successfully.",
            "data": business_category
        }
    
    def get_business_category_by_id(self, business_category_id: int, security_key: str):
        """Fetch a business category by its ID."""
        self.validate_security_key(security_key)
        business_category = self.business_category_repository.get_by_id(business_category_id)
        if not business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )
        return {
            "status": "success",
            "message": "Business Category retrieved successfully.",
            "data": business_category
        }
    def create_business_category(self, business_category_data: BusinessCategoryCreate, security_key: str, added_by: int):
        """Create a new business category."""
        self.validate_security_key(security_key)

        # Check if a business category with the same name already exists
        existing_business_category = self.business_category_repository.get_by_name(business_category_data.Business_Category_Name)
        if existing_business_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business Category with name '{business_category_data.Business_Category_Name}' already exists."
            )

        # Create the new business category
        new_business_category = self.business_category_repository.create(business_category_data, added_by)
        if not new_business_category:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Business Category."
            )
        return {
            "status": "success",
            "message": "Business Category created successfully.",
            "data": new_business_category
        }
    def update_business_category(self, business_category_id: int, business_category_data: BusinessCategoryUpdate, security_key: str,modified_by: int):
        """Update an existing business category."""
        self.validate_security_key(security_key)

        # Check if the business category exists
        existing_business_category = self.business_category_repository.get_by_id(business_category_id)
        if not existing_business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )
        if existing_business_category.Business_Category_Name != business_category_data.Business_Category_Name:
            # Check if a business category with the same name already exists
            duplicate_business_category = self.business_category_repository.get_by_name(business_category_data.Business_Category_Name)
            if duplicate_business_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Business Category with name '{business_category_data.Business_Category_Name}' already exists."
                )

        # Update the business category
        updated_business_category = self.business_category_repository.update(business_category_id, business_category_data, modified_by)
        if not updated_business_category:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update Business Category."
            )
        return {
            "status": "success",
            "message": "Business Category updated successfully.",
            "data": updated_business_category
        }
    def delete_business_category(self, business_category_id: int, security_key: str, deleted_by: int):
        """Delete a business category."""
        self.validate_security_key(security_key)

        # Check if the business category exists
        existing_business_category = self.business_category_repository.get_by_id(business_category_id)
        if not existing_business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )
        if existing_business_category.Is_Deleted == 'Y':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Business Category is already deleted."
            )

        # Delete the business category
        deleted_business_category = self.business_category_repository.delete(business_category_id, deleted_by)
        if not deleted_business_category:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete Business Category."
            )
        return {
            "status": "success",
            "message": "Business Category deleted successfully.",
            "data": deleted_business_category
        }