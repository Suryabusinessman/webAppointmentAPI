from fastapi import HTTPException, status, UploadFile
from app.repositories.BusinessModules.businesscategories import BusinessCategoryRepository
from app.schemas.BusinessModules.businesscategories import BusinessCategoryCreate, BusinessCategoryUpdate
from app.utils.file_upload import save_upload_file
from typing import Optional

UPLOAD_DIRECTORY_BUSINESS_CATEGORY_MEDIA = "uploads/business_category_media"
UPLOAD_DIRECTORY_BUSINESS_CATEGORY_ICONS = "uploads/business_category_icons"

class BusinessCategoryService:
    def __init__(self, business_category_repository: BusinessCategoryRepository, security_key: str):
        self.business_category_repository = business_category_repository
        self.security_key = security_key

    def get_all_business_categories(self, security_key: str):
        """Fetch all business categories."""
        business_categories = self.business_category_repository.get_all()
        return {
            "status": "success",
            "message": "Business Categories retrieved successfully.",
            "data": business_categories
        }
    
    def get_business_category_by_id(self, business_category_id: int, security_key: str):
        """Fetch a business category by its ID."""
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

    def create_business_category(self, business_type_id: int, business_category_name: str,
                               business_category_short_name: str, business_category_code: Optional[str] = None,
                               is_active: str = 'Y', business_category_description: Optional[str] = None,
                               business_category_media: Optional[UploadFile] = None, icon: Optional[UploadFile] = None,
                               secret_key: str = None, added_by: int = None):
        """Create a new business category."""
        # Check if a business category with the same name already exists
        existing_business_category = self.business_category_repository.get_by_name(business_category_name)
        if existing_business_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business Category with name '{business_category_name}' already exists."
            )

        # Handle file uploads
        business_category_media_path = None
        icon_path = None

        if business_category_media:
            business_category_media_path = save_upload_file(business_category_media, UPLOAD_DIRECTORY_BUSINESS_CATEGORY_MEDIA)

        if icon:
            icon_path = save_upload_file(icon, UPLOAD_DIRECTORY_BUSINESS_CATEGORY_ICONS)

        # Create business category data
        business_category_data = BusinessCategoryCreate(
            business_type_id=business_type_id,
            business_category_name=business_category_name,
            business_category_short_name=business_category_short_name,
            business_category_code=business_category_code,
            is_active=is_active,
            business_category_media=business_category_media_path,
            icon=icon_path,
            business_category_description=business_category_description
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

    def update_business_category(self, business_category_id: int, business_type_id: Optional[int] = None,
                               business_category_name: Optional[str] = None, business_category_short_name: Optional[str] = None,
                               business_category_code: Optional[str] = None, is_active: Optional[str] = None,
                               business_category_description: Optional[str] = None, business_category_media: Optional[UploadFile] = None,
                               icon: Optional[UploadFile] = None, secret_key: str = None, modified_by: int = None):
        """Update an existing business category."""
        # Check if the business category exists
        existing_business_category = self.business_category_repository.get_by_id(business_category_id)
        if not existing_business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )

        # Check if the new name already exists for another business category
        if business_category_name:
            duplicate_business_category = self.business_category_repository.get_by_name(business_category_name)
            if duplicate_business_category and duplicate_business_category.business_category_id != business_category_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Business Category with name '{business_category_name}' already exists."
                )

        # Handle file uploads - preserve existing files if no new files provided
        business_category_media_path = existing_business_category.business_category_media  # Keep existing file
        icon_path = existing_business_category.icon  # Keep existing file

        if business_category_media:
            business_category_media_path = save_upload_file(business_category_media, UPLOAD_DIRECTORY_BUSINESS_CATEGORY_MEDIA)

        if icon:
            icon_path = save_upload_file(icon, UPLOAD_DIRECTORY_BUSINESS_CATEGORY_ICONS)

        # Create update data
        update_data = BusinessCategoryUpdate(
            business_type_id=business_type_id,
            business_category_name=business_category_name,
            business_category_short_name=business_category_short_name,
            business_category_code=business_category_code,
            is_active=is_active,
            business_category_media=business_category_media_path,
            icon=icon_path,
            business_category_description=business_category_description
        )

        # Update the business category
        updated_business_category = self.business_category_repository.update(business_category_id, update_data, modified_by)
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
        # Ensure the business category exists
        business_category = self.business_category_repository.get_by_id(business_category_id)
        if not business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )

        # Perform the deletion
        result = self.business_category_repository.delete(business_category_id, deleted_by)
        return {
            "status": "success",
            "message": f"Business Category with ID {business_category_id} deleted successfully.",
            "data": result
        }

    def activate_business_category(self, business_category_id: int, security_key: str, modified_by: int):
        """Activate a business category."""
        activated_business_category = self.business_category_repository.activate_business_category(business_category_id, modified_by)
        return {
            "status": "success",
            "message": f"Business Category with ID {business_category_id} activated successfully.",
            "data": activated_business_category
        }

    def deactivate_business_category(self, business_category_id: int, security_key: str, modified_by: int):
        """Deactivate a business category."""
        deactivated_business_category = self.business_category_repository.deactivate_business_category(business_category_id, modified_by)
        return {
            "status": "success",
            "message": f"Business Category with ID {business_category_id} deactivated successfully.",
            "data": deactivated_business_category
        }

    def get_active_business_categories(self, security_key: str):
        """Get all active business categories."""
        business_categories = self.business_category_repository.get_active_business_categories()
        return {
            "status": "success",
            "message": "Active business categories retrieved successfully.",
            "data": business_categories
        }

    def get_inactive_business_categories(self, security_key: str):
        """Get all inactive business categories."""
        business_categories = self.business_category_repository.get_inactive_business_categories()
        return {
            "status": "success",
            "message": "Inactive business categories retrieved successfully.",
            "data": business_categories
        }