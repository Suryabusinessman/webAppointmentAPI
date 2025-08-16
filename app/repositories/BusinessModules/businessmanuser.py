from app.models.BusinessModules.businessmanuser import BusinessUser
from app.models.UserModules.users import User
from app.models.BusinessModules.businesstype import BusinessType
from app.schemas.BusinessModules.businessmanuser import BusinessUserCreate, BusinessUserUpdate
from sqlalchemy.orm import Session
from typing import List, Optional
from fastapi import HTTPException, status
from datetime import datetime

class BusinessmanUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[dict]:
        """Get all business users with user and business type information"""
        try:
            business_users = self.db.query(
                BusinessUser,
                User.full_name.label('user_full_name'),
                BusinessType.type_name.label('business_type_name')
            ).join(
                User, BusinessUser.user_id == User.user_id
            ).join(
                BusinessType, BusinessUser.business_type_id == BusinessType.business_type_id
            ).all()
            
            if not business_users:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="No business users found in the database."
                )
            
            # Convert to list of dictionaries with user and business type information
            result = []
            for business_user, user_full_name, business_type_name in business_users:
                # Split full name into first and last name
                name_parts = user_full_name.split(' ', 1) if user_full_name else ['', '']
                first_name = name_parts[0] if len(name_parts) > 0 else ''
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                business_user_dict = {
                    'business_user_id': business_user.business_user_id,
                    'user_id': business_user.user_id,
                    'business_type_id': business_user.business_type_id,
                    'business_name': business_user.business_name,
                    'business_description': business_user.business_description,
                    'business_logo': business_user.business_logo,
                    'business_banner': business_user.business_banner,
                    'business_address': business_user.business_address,
                    'business_phone': business_user.business_phone,
                    'business_email': business_user.business_email,
                    'business_website': business_user.business_website,
                    'gst_number': business_user.gst_number,
                    'pan_number': business_user.pan_number,
                    'business_license': business_user.business_license,
                    'subscription_plan': business_user.subscription_plan,
                    'subscription_status': business_user.subscription_status,
                    'subscription_start_date': business_user.subscription_start_date,
                    'subscription_end_date': business_user.subscription_end_date,
                    'monthly_limit': business_user.monthly_limit,
                    'current_month_usage': business_user.current_month_usage,
                    'is_verified': business_user.is_verified,
                    'is_active': business_user.is_active,
                    'is_featured': business_user.is_featured,
                    'rating': business_user.rating,
                    'total_reviews': business_user.total_reviews,
                    'created_at': business_user.created_at,
                    'updated_at': business_user.updated_at,
                    # User information
                    'user_full_name': user_full_name,
                    'user_first_name': first_name,
                    'user_last_name': last_name,
                    # Business type information
                    'business_type_name': business_type_name
                }
                result.append(business_user_dict)
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            # Check if it's a database connection error
            if "Can't connect to MySQL server" in str(e) or "Connection refused" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail="Database connection failed. Please ensure MySQL server is running."
                )
            elif "Access denied" in str(e):
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
                    detail="Database access denied. Please check database credentials."
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                    detail=f"Database error: {str(e)}"
                )

    def get_by_id(self, businessman_user_id: int) -> Optional[dict]:
        """Get business user by ID with user and business type information"""
        business_user = self.db.query(
            BusinessUser,
            User.full_name.label('user_full_name'),
            BusinessType.type_name.label('business_type_name')
        ).join(
            User, BusinessUser.user_id == User.user_id
        ).join(
            BusinessType, BusinessUser.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessUser.business_user_id == businessman_user_id
        ).first()
        
        if not business_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {businessman_user_id} not found."
            )
        
        # Convert to dictionary with user and business type information
        business_user_obj, user_full_name, business_type_name = business_user
        
        # Split full name into first and last name
        name_parts = user_full_name.split(' ', 1) if user_full_name else ['', '']
        first_name = name_parts[0] if len(name_parts) > 0 else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        result = {
            'business_user_id': business_user_obj.business_user_id,
            'user_id': business_user_obj.user_id,
            'business_type_id': business_user_obj.business_type_id,
            'business_name': business_user_obj.business_name,
            'business_description': business_user_obj.business_description,
            'business_logo': business_user_obj.business_logo,
            'business_banner': business_user_obj.business_banner,
            'business_address': business_user_obj.business_address,
            'business_phone': business_user_obj.business_phone,
            'business_email': business_user_obj.business_email,
            'business_website': business_user_obj.business_website,
            'gst_number': business_user_obj.gst_number,
            'pan_number': business_user_obj.pan_number,
            'business_license': business_user_obj.business_license,
            'subscription_plan': business_user_obj.subscription_plan,
            'subscription_status': business_user_obj.subscription_status,
            'subscription_start_date': business_user_obj.subscription_start_date,
            'subscription_end_date': business_user_obj.subscription_end_date,
            'monthly_limit': business_user_obj.monthly_limit,
            'current_month_usage': business_user_obj.current_month_usage,
            'is_verified': business_user_obj.is_verified,
            'is_active': business_user_obj.is_active,
            'is_featured': business_user_obj.is_featured,
            'rating': business_user_obj.rating,
            'total_reviews': business_user_obj.total_reviews,
            'created_at': business_user_obj.created_at,
            'updated_at': business_user_obj.updated_at,
            # User information
            'user_full_name': user_full_name,
            'user_first_name': first_name,
            'user_last_name': last_name,
            # Business type information
            'business_type_name': business_type_name
        }
        
        return result

    def get_by_id_object(self, businessman_user_id: int) -> Optional[BusinessUser]:
        """Get business user by ID as BusinessUser object (for internal operations)"""
        business_user = self.db.query(BusinessUser).filter(
            BusinessUser.business_user_id == businessman_user_id
        ).first()
        
        if not business_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {businessman_user_id} not found."
            )
        
        return business_user

    def get_by_email(self, email: str) -> Optional[BusinessUser]:
        """Get business user by email"""
        # This would need to join with User table to get email
        # For now, returning None as this is a placeholder
        return None
        #     user = self.db.query(BusinessUser).filter(
        #         BusinessUser.email == email,
        #         BusinessUser.is_deleted == 'N'
        #     ).first()
        #     return user

    def get_by_business_type_and_user(self, business_type_id: int, user_id: int) -> Optional[BusinessUser]:
        """Get business user by business type and user ID"""
        return self.db.query(BusinessUser).filter(
            BusinessUser.business_type_id == business_type_id,
            BusinessUser.user_id == user_id
        ).first()

    def create(self, business_man_user_data: BusinessUserCreate, added_by: int):
        """Create a new business user"""
        # Check for existing business user with same user_id and business_type_id
        existing_business_man_user = self.db.query(BusinessUser).filter(
            BusinessUser.user_id == business_man_user_data.user_id,
            BusinessUser.business_type_id == business_man_user_data.business_type_id
        ).first()

        if existing_business_man_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Business user already exists with this user and business type combination"
            )

        new_business_user = BusinessUser(
            user_id=business_man_user_data.user_id,
            business_type_id=business_man_user_data.business_type_id,
            business_name=business_man_user_data.business_name,
            business_description=business_man_user_data.business_description,
            business_logo=business_man_user_data.business_logo,
            business_banner=business_man_user_data.business_banner,
            business_address=business_man_user_data.business_address,
            business_phone=business_man_user_data.business_phone,
            business_email=business_man_user_data.business_email,
            business_website=business_man_user_data.business_website,
            gst_number=business_man_user_data.gst_number,
            pan_number=business_man_user_data.pan_number,
            business_license=business_man_user_data.business_license,
            subscription_plan=business_man_user_data.subscription_plan,
            subscription_status=business_man_user_data.subscription_status,
            subscription_start_date=business_man_user_data.subscription_start_date,
            subscription_end_date=business_man_user_data.subscription_end_date,
            monthly_limit=business_man_user_data.monthly_limit,
            current_month_usage=business_man_user_data.current_month_usage,
            is_verified=business_man_user_data.is_verified,
            is_active=business_man_user_data.is_active,
            is_featured=business_man_user_data.is_featured,
            rating=business_man_user_data.rating,
            total_reviews=business_man_user_data.total_reviews
        )

        self.db.add(new_business_user)
        self.db.commit()
        self.db.refresh(new_business_user)
        return new_business_user

    def update(self, business_man_user_id: int, business_man_user_data: BusinessUserUpdate, modified_by: int):
        """Update an existing business user"""
        business_user = self.get_by_id_object(business_man_user_id)  # Ensure the business user exists

        # Update fields if provided
        if business_man_user_data.user_id is not None:
            business_user.user_id = business_man_user_data.user_id
        if business_man_user_data.business_type_id is not None:
            business_user.business_type_id = business_man_user_data.business_type_id
        if business_man_user_data.business_name is not None:
            business_user.business_name = business_man_user_data.business_name
        if business_man_user_data.business_description is not None:
            business_user.business_description = business_man_user_data.business_description
        if business_man_user_data.business_logo is not None:
            business_user.business_logo = business_man_user_data.business_logo
        if business_man_user_data.business_banner is not None:
            business_user.business_banner = business_man_user_data.business_banner
        if business_man_user_data.business_address is not None:
            business_user.business_address = business_man_user_data.business_address
        if business_man_user_data.business_phone is not None:
            business_user.business_phone = business_man_user_data.business_phone
        if business_man_user_data.business_email is not None:
            business_user.business_email = business_man_user_data.business_email
        if business_man_user_data.business_website is not None:
            business_user.business_website = business_man_user_data.business_website
        if business_man_user_data.gst_number is not None:
            business_user.gst_number = business_man_user_data.gst_number
        if business_man_user_data.pan_number is not None:
            business_user.pan_number = business_man_user_data.pan_number
        if business_man_user_data.business_license is not None:
            business_user.business_license = business_man_user_data.business_license
        if business_man_user_data.subscription_plan is not None:
            business_user.subscription_plan = business_man_user_data.subscription_plan
        if business_man_user_data.subscription_status is not None:
            business_user.subscription_status = business_man_user_data.subscription_status
        if business_man_user_data.subscription_start_date is not None:
            business_user.subscription_start_date = business_man_user_data.subscription_start_date
        if business_man_user_data.subscription_end_date is not None:
            business_user.subscription_end_date = business_man_user_data.subscription_end_date
        if business_man_user_data.monthly_limit is not None:
            business_user.monthly_limit = business_man_user_data.monthly_limit
        if business_man_user_data.current_month_usage is not None:
            business_user.current_month_usage = business_man_user_data.current_month_usage
        if business_man_user_data.is_verified is not None:
            business_user.is_verified = business_man_user_data.is_verified
        if business_man_user_data.is_active is not None:
            business_user.is_active = business_man_user_data.is_active
        if business_man_user_data.is_featured is not None:
            business_user.is_featured = business_man_user_data.is_featured
        if business_man_user_data.rating is not None:
            business_user.rating = business_man_user_data.rating
        if business_man_user_data.total_reviews is not None:
            business_user.total_reviews = business_man_user_data.total_reviews

        # The updated_at field is automatically updated by SQLAlchemy

        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def delete(self, business_man_user_id: int, deleted_by: int):
        """Soft delete a business user"""
        business_user = self.get_by_id_object(business_man_user_id)  # Ensure the business user exists

        # Perform a soft delete by setting is_active to 'N'
        business_user.is_active = 'N'

        self.db.commit()
        return business_user

    def activate_businessman_user(self, businessman_user_id: int, modified_by: int):
        """Activate a business user."""
        business_user = self.get_by_id_object(businessman_user_id)  # Ensure the business user exists
        
        # Activate the business user
        business_user.is_active = 'Y'

        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def deactivate_businessman_user(self, businessman_user_id: int, modified_by: int):
        """Deactivate a business user."""
        business_user = self.get_by_id_object(businessman_user_id)
        business_user.is_active = 'N'
        business_user.modified_by = modified_by
        business_user.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def verify_businessman_user(self, businessman_user_id: int, modified_by: int):
        """Verify a business user."""
        business_user = self.get_by_id_object(businessman_user_id)
        business_user.is_verified = 'Y'
        business_user.modified_by = modified_by
        business_user.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def unverify_businessman_user(self, businessman_user_id: int, modified_by: int):
        """Unverify a business user."""
        business_user = self.get_by_id_object(businessman_user_id)
        business_user.is_verified = 'N'
        business_user.modified_by = modified_by
        business_user.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def feature_businessman_user(self, businessman_user_id: int, modified_by: int):
        """Feature a business user."""
        business_user = self.get_by_id_object(businessman_user_id)
        business_user.is_featured = 'Y'
        business_user.modified_by = modified_by
        business_user.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def unfeature_businessman_user(self, businessman_user_id: int, modified_by: int):
        """Unfeature a business user."""
        business_user = self.get_by_id_object(businessman_user_id)
        business_user.is_featured = 'N'
        business_user.modified_by = modified_by
        business_user.modified_on = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(business_user)
        return business_user

    def get_active_businessman_users(self) -> List[dict]:
        """Get all active business users with user and business type information"""
        business_users = self.db.query(
            BusinessUser,
            User.full_name.label('user_full_name'),
            BusinessType.type_name.label('business_type_name')
        ).join(
            User, BusinessUser.user_id == User.user_id
        ).join(
            BusinessType, BusinessUser.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessUser.is_active == 'Y'
        ).all()
        
        if not business_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active business users found in the database."
            )
        
        # Convert to list of dictionaries with user and business type information
        result = []
        for business_user, user_full_name, business_type_name in business_users:
            # Split full name into first and last name
            name_parts = user_full_name.split(' ', 1) if user_full_name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            business_user_dict = {
                'business_user_id': business_user.business_user_id,
                'user_id': business_user.user_id,
                'business_type_id': business_user.business_type_id,
                'business_name': business_user.business_name,
                'business_description': business_user.business_description,
                'business_logo': business_user.business_logo,
                'business_banner': business_user.business_banner,
                'business_address': business_user.business_address,
                'business_phone': business_user.business_phone,
                'business_email': business_user.business_email,
                'business_website': business_user.business_website,
                'gst_number': business_user.gst_number,
                'pan_number': business_user.pan_number,
                'business_license': business_user.business_license,
                'subscription_plan': business_user.subscription_plan,
                'subscription_status': business_user.subscription_status,
                'subscription_start_date': business_user.subscription_start_date,
                'subscription_end_date': business_user.subscription_end_date,
                'monthly_limit': business_user.monthly_limit,
                'current_month_usage': business_user.current_month_usage,
                'is_verified': business_user.is_verified,
                'is_active': business_user.is_active,
                'is_featured': business_user.is_featured,
                'rating': business_user.rating,
                'total_reviews': business_user.total_reviews,
                'created_at': business_user.created_at,
                'updated_at': business_user.updated_at,
                # User information
                'user_full_name': user_full_name,
                'user_first_name': first_name,
                'user_last_name': last_name,
                # Business type information
                'business_type_name': business_type_name
            }
            result.append(business_user_dict)
        
        return result

    def get_inactive_businessman_users(self) -> List[dict]:
        """Get all inactive business users with user and business type information"""
        business_users = self.db.query(
            BusinessUser,
            User.full_name.label('user_full_name'),
            BusinessType.type_name.label('business_type_name')
        ).join(
            User, BusinessUser.user_id == User.user_id
        ).join(
            BusinessType, BusinessUser.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessUser.is_active == 'N'
        ).all()
        
        if not business_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No inactive business users found in the database."
            )
        
        # Convert to list of dictionaries with user and business type information
        result = []
        for business_user, user_full_name, business_type_name in business_users:
            # Split full name into first and last name
            name_parts = user_full_name.split(' ', 1) if user_full_name else ['', '']
            first_name = name_parts[0] if len(name_parts) > 0 else ''
            last_name = name_parts[1] if len(name_parts) > 1 else ''
            
            business_user_dict = {
                'business_user_id': business_user.business_user_id,
                'user_id': business_user.user_id,
                'business_type_id': business_user.business_type_id,
                'business_name': business_user.business_name,
                'business_description': business_user.business_description,
                'business_logo': business_user.business_logo,
                'business_banner': business_user.business_banner,
                'business_address': business_user.business_address,
                'business_phone': business_user.business_phone,
                'business_email': business_user.business_email,
                'business_website': business_user.business_website,
                'gst_number': business_user.gst_number,
                'pan_number': business_user.pan_number,
                'business_license': business_user.business_license,
                'subscription_plan': business_user.subscription_plan,
                'subscription_status': business_user.subscription_status,
                'subscription_start_date': business_user.subscription_start_date,
                'subscription_end_date': business_user.subscription_end_date,
                'monthly_limit': business_user.monthly_limit,
                'current_month_usage': business_user.current_month_usage,
                'is_verified': business_user.is_verified,
                'is_active': business_user.is_active,
                'is_featured': business_user.is_featured,
                'rating': business_user.rating,
                'total_reviews': business_user.total_reviews,
                'created_at': business_user.created_at,
                'updated_at': business_user.updated_at,
                # User information
                'user_full_name': user_full_name,
                'user_first_name': first_name,
                'user_last_name': last_name,
                # Business type information
                'business_type_name': business_type_name
            }
            result.append(business_user_dict)
        
        return result