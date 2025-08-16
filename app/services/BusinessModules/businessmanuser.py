from fastapi import HTTPException, status, UploadFile
from typing import List, Optional
from app.repositories.BusinessModules.businessmanuser import BusinessmanUserRepository
from app.schemas.BusinessModules.businessmanuser import BusinessUserCreate, BusinessUserUpdate, BusinessUserCreateMultiple
from app.utils.file_upload import save_upload_file
from datetime import datetime

UPLOAD_DIRECTORY_BUSINESS_LOGOS = "uploads/business_logos"
UPLOAD_DIRECTORY_BUSINESS_BANNERS = "uploads/business_banners"

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
        """Fetch all business users."""
        businessman_user = self.businessman_user_repository.get_all()
        return {
            "status": "success",
            "message": "Business users retrieved successfully.",
            "data": businessman_user
        }

    def get_businessman_user_by_id(self, businessman_user_id: int, security_key: str):
        """Fetch a business user by its ID."""
        businessman_user = self.businessman_user_repository.get_by_id(businessman_user_id)
        if not businessman_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business User with ID {businessman_user_id} not found."
            )
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} retrieved successfully.",
            "data": businessman_user
        }

    def create_businessman_user(self, user_id: int, business_type_id: int,
                               business_name: str, business_description: Optional[str] = None,
                               business_address: Optional[str] = None, business_phone: Optional[str] = None,
                               business_email: Optional[str] = None, business_website: Optional[str] = None,
                               gst_number: Optional[str] = None, pan_number: Optional[str] = None,
                               business_license: Optional[str] = None, subscription_plan: str = "FREE",
                               subscription_status: str = "Active", subscription_start_date: Optional[datetime] = None,
                               subscription_end_date: Optional[datetime] = None, monthly_limit: Optional[int] = None,
                               current_month_usage: int = 0, is_verified: str = "N", is_active: str = "Y",
                               is_featured: str = "N", rating: float = 0.0, total_reviews: int = 0,
                               business_logo: Optional[UploadFile] = None, business_banner: Optional[UploadFile] = None,
                               secret_key: str = None, added_by: int = None):
        """Create a new business user."""
        # Check if a business user with the same user and business type already exists
        existing_businessman_user = self.businessman_user_repository.get_by_business_type_and_user(
            business_type_id=business_type_id,
            user_id=user_id
        )
        if existing_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Business User with this user and business type combination already exists."
            )

        # Handle file uploads
        business_logo_path = None
        business_banner_path = None

        if business_logo:
            business_logo_path = save_upload_file(business_logo, UPLOAD_DIRECTORY_BUSINESS_LOGOS)

        if business_banner:
            business_banner_path = save_upload_file(business_banner, UPLOAD_DIRECTORY_BUSINESS_BANNERS)

        # Create business user data
        businessman_user_data = BusinessUserCreate(
            user_id=user_id,
            business_type_id=business_type_id,
            business_name=business_name,
            business_description=business_description,
            business_logo=business_logo_path,
            business_banner=business_banner_path,
            business_address=business_address,
            business_phone=business_phone,
            business_email=business_email,
            business_website=business_website,
            gst_number=gst_number,
            pan_number=pan_number,
            business_license=business_license,
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            subscription_start_date=subscription_start_date,
            subscription_end_date=subscription_end_date,
            monthly_limit=monthly_limit,
            current_month_usage=current_month_usage,
            is_verified=is_verified,
            is_active=is_active,
            is_featured=is_featured,
            rating=rating,
            total_reviews=total_reviews
        )

        # Create the new business user
        new_businessman_user = self.businessman_user_repository.create(businessman_user_data, added_by)
        if not new_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create Business User."
            )

        return {
            "status": "success",
            "message": "Business User created successfully.",
            "data": new_businessman_user
        }

    def create_multiple_business_users_by_types(self, user_id: int, business_type_ids: List[int],
                                               business_name: str, business_description: Optional[str] = None,
                                               business_address: Optional[str] = None, business_phone: Optional[str] = None,
                                               business_email: Optional[str] = None, business_website: Optional[str] = None,
                                               gst_number: Optional[str] = None, pan_number: Optional[str] = None,
                                               business_license: Optional[str] = None, subscription_plan: str = "FREE",
                                               subscription_status: str = "Active", subscription_start_date: Optional[datetime] = None,
                                               subscription_end_date: Optional[datetime] = None, monthly_limit: Optional[int] = None,
                                               current_month_usage: int = 0, is_verified: str = "N", is_active: str = "Y",
                                               is_featured: str = "N", rating: float = 0.0, total_reviews: int = 0,
                                               business_logo: Optional[UploadFile] = None, business_banner: Optional[UploadFile] = None,
                                               secret_key: str = None, added_by: int = None):
        """Create multiple business users for multiple business types."""
        if not business_type_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one business type ID is required."
            )

        # Handle file uploads once
        business_logo_path = None
        business_banner_path = None

        if business_logo:
            business_logo_path = save_upload_file(business_logo, UPLOAD_DIRECTORY_BUSINESS_LOGOS)

        if business_banner:
            business_banner_path = save_upload_file(business_banner, UPLOAD_DIRECTORY_BUSINESS_BANNERS)

        created_users = []
        failed_creations = []

        for business_type_id in business_type_ids:
            try:
                # Check if a business user with the same user and business type already exists
                existing_businessman_user = self.businessman_user_repository.get_by_business_type_and_user(
                    business_type_id=business_type_id,
                    user_id=user_id
                )
                if existing_businessman_user:
                    failed_creations.append({
                        "business_type_id": business_type_id,
                        "reason": "Business User with this user and business type combination already exists."
                    })
                    continue

                # Create business user data for this business type
                businessman_user_data = BusinessUserCreate(
                    user_id=user_id,
                    business_type_id=business_type_id,
                    business_name=business_name,
                    business_description=business_description,
                    business_logo=business_logo_path,
                    business_banner=business_banner_path,
                    business_address=business_address,
                    business_phone=business_phone,
                    business_email=business_email,
                    business_website=business_website,
                    gst_number=gst_number,
                    pan_number=pan_number,
                    business_license=business_license,
                    subscription_plan=subscription_plan,
                    subscription_status=subscription_status,
                    subscription_start_date=subscription_start_date,
                    subscription_end_date=subscription_end_date,
                    monthly_limit=monthly_limit,
                    current_month_usage=current_month_usage,
                    is_verified=is_verified,
                    is_active=is_active,
                    is_featured=is_featured,
                    rating=rating,
                    total_reviews=total_reviews
                )

                # Create the new business user
                new_businessman_user = self.businessman_user_repository.create(businessman_user_data, added_by)
                if new_businessman_user:
                    created_users.append(new_businessman_user)
                else:
                    failed_creations.append({
                        "business_type_id": business_type_id,
                        "reason": "Failed to create Business User."
                    })

            except Exception as e:
                failed_creations.append({
                    "business_type_id": business_type_id,
                    "reason": str(e)
                })

        return {
            "status": "success",
            "message": f"Created {len(created_users)} business users. {len(failed_creations)} failed.",
            "data": {
                "created_users": created_users,
                "failed_creations": failed_creations,
                "total_requested": len(business_type_ids),
                "total_created": len(created_users),
                "total_failed": len(failed_creations)
            }
        }

    def create_multiple_businessman_users(
        self,
        users_data: List[BusinessUserCreate],
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
                if not data.business_type_id or not data.business_name:
                    results["failed"].append({
                        "index": index,
                        "reason": "Missing business_type_id or business_name"
                    })
                    continue

                # Insert record
                user = self.create_businessman_user(
                    user_id=data.user_id,
                    business_type_id=data.business_type_id,
                    business_name=data.business_name,
                    business_description=data.business_description,
                    business_address=data.business_address,
                    business_phone=data.business_phone,
                    business_email=data.business_email,
                    business_website=data.business_website,
                    gst_number=data.gst_number,
                    pan_number=data.pan_number,
                    business_license=data.business_license,
                    subscription_plan=data.subscription_plan,
                    subscription_status=data.subscription_status,
                    subscription_start_date=data.subscription_start_date,
                    subscription_end_date=data.subscription_end_date,
                    monthly_limit=data.monthly_limit,
                    current_month_usage=data.current_month_usage,
                    is_verified=data.is_verified,
                    is_active=data.is_active,
                    is_featured=data.is_featured,
                    rating=data.rating,
                    total_reviews=data.total_reviews,
                    secret_key=security_key,
                    added_by=added_by
                )
                if user and user.get("data"):
                    results["success"].append(user["data"])
                else:
                    results["failed"].append({
                        "index": index,
                        "reason": "Failed to create business user"
                    })

            except Exception as e:
                results["failed"].append({
                    "index": index,
                    "reason": str(e)
                })

        return {
            "status": "success",
            "message": f"Processed {len(users_data)} business users. {len(results['success'])} successful, {len(results['failed'])} failed.",
            "data": results
        }

    def update_businessman_user(self, businessman_user_id: int, user_id: Optional[int] = None,
                               business_type_id: Optional[int] = None,
                               business_name: Optional[str] = None, business_description: Optional[str] = None,
                               business_address: Optional[str] = None, business_phone: Optional[str] = None,
                               business_email: Optional[str] = None, business_website: Optional[str] = None,
                               gst_number: Optional[str] = None, pan_number: Optional[str] = None,
                               business_license: Optional[str] = None, subscription_plan: Optional[str] = None,
                               subscription_status: Optional[str] = None, subscription_start_date: Optional[datetime] = None,
                               subscription_end_date: Optional[datetime] = None, monthly_limit: Optional[int] = None,
                               current_month_usage: Optional[int] = None, is_verified: Optional[str] = None,
                               is_active: Optional[str] = None, is_featured: Optional[str] = None,
                               rating: Optional[float] = None, total_reviews: Optional[int] = None,
                               business_logo: Optional[UploadFile] = None, business_banner: Optional[UploadFile] = None,
                               secret_key: str = None, updated_by: int = None):
        """Update an existing business user."""
        # Check if the business user exists
        existing_businessman_user = self.businessman_user_repository.get_by_id(businessman_user_id)
        if not existing_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business User with ID {businessman_user_id} not found."
            )

        # Handle file uploads - preserve existing files if no new files provided
        # Note: get_by_id now returns a dictionary, so we access it differently
        business_logo_path = existing_businessman_user.get('business_logo')  # Keep existing file
        business_banner_path = existing_businessman_user.get('business_banner')  # Keep existing file

        if business_logo:
            business_logo_path = save_upload_file(business_logo, UPLOAD_DIRECTORY_BUSINESS_LOGOS)

        if business_banner:
            business_banner_path = save_upload_file(business_banner, UPLOAD_DIRECTORY_BUSINESS_BANNERS)

        # Create update data
        update_data = BusinessUserUpdate(
            user_id=user_id,
            business_type_id=business_type_id,
            business_name=business_name,
            business_description=business_description,
            business_logo=business_logo_path,
            business_banner=business_banner_path,
            business_address=business_address,
            business_phone=business_phone,
            business_email=business_email,
            business_website=business_website,
            gst_number=gst_number,
            pan_number=pan_number,
            business_license=business_license,
            subscription_plan=subscription_plan,
            subscription_status=subscription_status,
            subscription_start_date=subscription_start_date,
            subscription_end_date=subscription_end_date,
            monthly_limit=monthly_limit,
            current_month_usage=current_month_usage,
            is_verified=is_verified,
            is_active=is_active,
            is_featured=is_featured,
            rating=rating,
            total_reviews=total_reviews
        )

        # Update the business user
        updated_businessman_user = self.businessman_user_repository.update(businessman_user_id, update_data, updated_by)
        if not updated_businessman_user:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update Business User."
            )

        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} updated successfully.",
            "data": updated_businessman_user
        }

    def delete_businessman_user(self, businessman_user_id: int, security_key: str, deleted_by: int):
        """Delete a business user."""
        # Ensure the business user exists
        businessman_user = self.businessman_user_repository.get_by_id(businessman_user_id)
        if not businessman_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business User with ID {businessman_user_id} not found."
            )

        # Perform the deletion
        result = self.businessman_user_repository.delete(businessman_user_id, deleted_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} deleted successfully.",
            "data": result
        }

    def activate_businessman_user(self, businessman_user_id: int, security_key: str, modified_by: int):
        """Activate a business user."""
        activated_businessman_user = self.businessman_user_repository.activate_businessman_user(businessman_user_id, modified_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} activated successfully.",
            "data": activated_businessman_user
        }

    def deactivate_businessman_user(self, businessman_user_id: int, security_key: str, modified_by: int):
        """Deactivate a business user."""
        deactivated_businessman_user = self.businessman_user_repository.deactivate_businessman_user(businessman_user_id, modified_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} deactivated successfully.",
            "data": deactivated_businessman_user
        }

    def verify_businessman_user(self, businessman_user_id: int, security_key: str, modified_by: int):
        """Verify a business user."""
        verified_businessman_user = self.businessman_user_repository.verify_businessman_user(businessman_user_id, modified_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} verified successfully.",
            "data": verified_businessman_user
        }

    def unverify_businessman_user(self, businessman_user_id: int, security_key: str, modified_by: int):
        """Unverify a business user."""
        unverified_businessman_user = self.businessman_user_repository.unverify_businessman_user(businessman_user_id, modified_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} unverified successfully.",
            "data": unverified_businessman_user
        }

    def feature_businessman_user(self, businessman_user_id: int, security_key: str, modified_by: int):
        """Feature a business user."""
        featured_businessman_user = self.businessman_user_repository.feature_businessman_user(businessman_user_id, modified_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} featured successfully.",
            "data": featured_businessman_user
        }

    def unfeature_businessman_user(self, businessman_user_id: int, security_key: str, modified_by: int):
        """Unfeature a business user."""
        unfeatured_businessman_user = self.businessman_user_repository.unfeature_businessman_user(businessman_user_id, modified_by)
        return {
            "status": "success",
            "message": f"Business User with ID {businessman_user_id} unfeatured successfully.",
            "data": unfeatured_businessman_user
        }

    def get_active_businessman_users(self, security_key: str):
        """Get all active business users."""
        businessman_users = self.businessman_user_repository.get_active_businessman_users()
        return {
            "status": "success",
            "message": "Active business users retrieved successfully.",
            "data": businessman_users
        }

    def get_inactive_businessman_users(self, security_key: str):
        """Get all inactive business users."""
        businessman_users = self.businessman_user_repository.get_inactive_businessman_users()
        return {
            "status": "success",
            "message": "Inactive business users retrieved successfully.",
            "data": businessman_users
        }

