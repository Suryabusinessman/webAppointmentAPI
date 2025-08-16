from fastapi import HTTPException, status, UploadFile
from app.repositories.BusinessModules.businesstype import BusinessTypeRepository
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate, BusinessTypeResponse
from app.utils.file_upload import save_upload_file
from typing import Optional
import json

UPLOAD_DIRECTORY_BUSINESS_MEDIA = "uploads/business_media"
UPLOAD_DIRECTORY_ICONS = "uploads/business_icons"

class BusinessTypeService:
    def __init__(self, business_type_repository: BusinessTypeRepository, security_key: str):
        self.business_type_repository = business_type_repository
        self.security_key = security_key

    def get_all_business_types(self, security_key: str):
        """Fetch all business types."""
        business_types = self.business_type_repository.get_all()
        return {
            "status": "success",
            "message": "Business types retrieved successfully.",
            "data": business_types
        }

    def get_business_type_by_id(self, business_type_id: int, security_key: str):
        """Fetch a business type by its ID."""
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

    def create_business_type(self, type_name: str, description: Optional[str] = None, 
                           color: Optional[str] = None, features: Optional[str] = None,
                           is_active: str = 'Y', business_media: Optional[UploadFile] = None,
                           icon: Optional[UploadFile] = None, secret_key: str = None, added_by: int = None):
        """Create a new business type."""
        # Check if a business type with the same name already exists
        existing_business_type = self.business_type_repository.get_by_name(type_name)
        if existing_business_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business Type with name '{type_name}' already exists."
            )

        # Handle file uploads
        business_media_path = None
        icon_path = None

        if business_media:
            business_media_path = save_upload_file(business_media, UPLOAD_DIRECTORY_BUSINESS_MEDIA)

        if icon:
            icon_path = save_upload_file(icon, UPLOAD_DIRECTORY_ICONS)

        # Handle features - store as string if not valid JSON
        features_dict = None
        if features:
            # Try to parse as JSON, if it fails, store as string
            try:
                features_dict = json.loads(features)
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, store the string as is
                features_dict = features

        # Create business type data
        business_type_data = BusinessTypeCreate(
            type_name=type_name,
            description=description,
            icon=icon_path,
            color=color,
            features=features_dict,
            business_media=business_media_path,
            is_active=is_active
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

    def update_business_type(self, business_type_id: int, type_name: Optional[str] = None,
                           description: Optional[str] = None, color: Optional[str] = None,
                           features: Optional[str] = None, is_active: Optional[str] = None,
                           business_media: Optional[UploadFile] = None, icon: Optional[UploadFile] = None,
                           secret_key: str = None, modified_by: int = None):
        """Update an existing business type."""
        # Ensure the business type exists
        business_type = self.business_type_repository.get_by_id(business_type_id)
        if not business_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Type with ID {business_type_id} not found."
            )

        # Prevent updating to a duplicate name
        if type_name:
            existing_business_type = self.business_type_repository.get_by_name(type_name)
            if existing_business_type and existing_business_type.business_type_id != business_type_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Another business type with name '{type_name}' already exists."
                )

        # Handle file uploads - preserve existing files if no new files provided
        business_media_path = business_type.business_media  # Keep existing file
        icon_path = business_type.icon  # Keep existing file

        if business_media:
            business_media_path = save_upload_file(business_media, UPLOAD_DIRECTORY_BUSINESS_MEDIA)

        if icon:
            icon_path = save_upload_file(icon, UPLOAD_DIRECTORY_ICONS)

        # Handle features - store as string if not valid JSON
        features_dict = None
        if features:
            # Try to parse as JSON, if it fails, store as string
            try:
                features_dict = json.loads(features)
            except (json.JSONDecodeError, TypeError):
                # If it's not valid JSON, store the string as is
                features_dict = features

        # Create update data
        update_data = BusinessTypeUpdate(
            type_name=type_name,
            description=description,
            icon=icon_path,
            color=color,
            features=features_dict,
            business_media=business_media_path,
            is_active=is_active
        )

        # Update the business type
        updated_business_type = self.business_type_repository.update(business_type_id, update_data, modified_by)
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
            "message": f"Business Type with ID {business_type_id} deleted successfully.",
            "data": result
        }

    def activate_business_type(self, business_type_id: int, security_key: str, modified_by: int):
        """Activate a business type."""
        activated_business_type = self.business_type_repository.activate_business_type(business_type_id, modified_by)
        return {
            "status": "success",
            "message": f"Business Type with ID {business_type_id} activated successfully.",
            "data": activated_business_type
        }

    def deactivate_business_type(self, business_type_id: int, security_key: str, modified_by: int):
        """Deactivate a business type."""
        deactivated_business_type = self.business_type_repository.deactivate_business_type(business_type_id, modified_by)
        return {
            "status": "success",
            "message": f"Business Type with ID {business_type_id} deactivated successfully.",
            "data": deactivated_business_type
        }

    def get_active_business_types(self, security_key: str):
        """Get all active business types."""
        business_types = self.business_type_repository.get_active_business_types()
        return {
            "status": "success",
            "message": "Active business types retrieved successfully.",
            "data": business_types
        }

    def get_inactive_business_types(self, security_key: str):
        """Get all inactive business types."""
        business_types = self.business_type_repository.get_inactive_business_types()
        return {
            "status": "success",
            "message": "Inactive business types retrieved successfully.",
            "data": business_types
        }