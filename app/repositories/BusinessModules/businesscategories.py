from sqlalchemy.orm import Session
from app.models.BusinessModules.businesscategory import BusinessCategory
from app.models.BusinessModules.businesstype import BusinessType
from app.schemas.BusinessModules.businesscategories import BusinessCategoryCreate, BusinessCategoryUpdate
from fastapi import HTTPException, status
from datetime import datetime

class BusinessCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active business categories with business type names."""
        business_categories = self.db.query(
            BusinessCategory,
            BusinessType.type_name.label('business_type_name')
        ).join(
            BusinessType, 
            BusinessCategory.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessCategory.is_deleted == 'N'
        ).all()
        
        if not business_categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Business categories found in the database."
            )
        
        # Convert to list of dictionaries with business type name
        result = []
        for category, business_type_name in business_categories:
            category_dict = {
                'business_category_id': category.business_category_id,
                'business_type_id': category.business_type_id,
                'business_type_name': business_type_name,
                'business_category_name': category.business_category_name,
                'business_category_short_name': category.business_category_short_name,
                'business_category_code': category.business_category_code,
                'is_active': category.is_active,
                'business_category_media': category.business_category_media,
                'icon': category.icon,
                'business_category_description': category.business_category_description,
                'added_by': category.added_by,
                'added_on': category.added_on,
                'modified_by': category.modified_by,
                'modified_on': category.modified_on,
                'is_deleted': category.is_deleted,
                'deleted_by': category.deleted_by,
                'deleted_on': category.deleted_on
            }
            result.append(category_dict)
        
        return result

    def get_by_id(self, business_category_id: int):
        """Fetch a business category by its ID with business type name."""
        business_category = self.db.query(
            BusinessCategory,
            BusinessType.type_name.label('business_type_name')
        ).join(
            BusinessType, 
            BusinessCategory.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessCategory.business_category_id == business_category_id,
            BusinessCategory.is_deleted == 'N'
        ).first()
        
        if not business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )
        
        # Convert to dictionary with business type name
        category, business_type_name = business_category
        result = {
            'business_category_id': category.business_category_id,
            'business_type_id': category.business_type_id,
            'business_type_name': business_type_name,
            'business_category_name': category.business_category_name,
            'business_category_short_name': category.business_category_short_name,
            'business_category_code': category.business_category_code,
            'is_active': category.is_active,
            'business_category_media': category.business_category_media,
            'icon': category.icon,
            'business_category_description': category.business_category_description,
            'added_by': category.added_by,
            'added_on': category.added_on,
            'modified_by': category.modified_by,
            'modified_on': category.modified_on,
            'is_deleted': category.is_deleted,
            'deleted_by': category.deleted_by,
            'deleted_on': category.deleted_on
        }
        
        return result

    def get_by_name(self, business_category_name: str):
        """Fetch a business category by its name."""
        business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.business_category_name == business_category_name,
            BusinessCategory.is_deleted == 'N'
        ).first()
        return business_category

    def create(self, business_category_data: BusinessCategoryCreate, added_by: int):
        """Create a new business category."""
        # Check if a business category with the same name already exists
        existing_business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.business_category_name == business_category_data.business_category_name,
            BusinessCategory.is_deleted == 'N'
        ).first()

        if existing_business_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Business Category with name '{business_category_data.business_category_name}' already exists."
            )

        # Create the new business category
        new_business_category = BusinessCategory(
            business_type_id=business_category_data.business_type_id,
            business_category_name=business_category_data.business_category_name,
            business_category_short_name=business_category_data.business_category_short_name,
            business_category_code=business_category_data.business_category_code,
            is_active=business_category_data.is_active,
            business_category_media=business_category_data.business_category_media,
            icon=business_category_data.icon,
            business_category_description=business_category_data.business_category_description,
            added_by=added_by,
            added_on=datetime.utcnow(),
            is_deleted='N'
        )
        self.db.add(new_business_category)
        self.db.commit()
        self.db.refresh(new_business_category)
        return new_business_category

    def update(self, business_category_id: int, business_category_data: BusinessCategoryUpdate, modified_by: int):
        """Update an existing business category."""
        business_category = self.get_by_id(business_category_id)  # Ensure the business category exists

        # Update fields if provided
        if business_category_data.business_type_id is not None:
            business_category.business_type_id = business_category_data.business_type_id
        if business_category_data.business_category_name is not None:
            business_category.business_category_name = business_category_data.business_category_name
        if business_category_data.business_category_short_name is not None:
            business_category.business_category_short_name = business_category_data.business_category_short_name
        if business_category_data.business_category_code is not None:
            business_category.business_category_code = business_category_data.business_category_code
        if business_category_data.is_active is not None:
            business_category.is_active = business_category_data.is_active
        if business_category_data.business_category_media is not None:
            business_category.business_category_media = business_category_data.business_category_media
        if business_category_data.icon is not None:
            business_category.icon = business_category_data.icon
        if business_category_data.business_category_description is not None:
            business_category.business_category_description = business_category_data.business_category_description

        # Update audit fields
        business_category.modified_by = modified_by
        business_category.modified_on = datetime.utcnow()

        self.db.commit()
        self.db.refresh(business_category)
        return business_category

    def delete(self, business_category_id: int, deleted_by: int):
        """Soft delete a business category."""
        business_category = self.get_by_id(business_category_id)  # Ensure the business category exists

        # Perform a soft delete
        business_category.is_deleted = 'Y'
        business_category.deleted_by = deleted_by
        business_category.deleted_on = datetime.utcnow()

        self.db.commit()
        return business_category

    def activate_business_category(self, business_category_id: int, modified_by: int):
        """Activate a business category."""
        business_category = self.get_by_id(business_category_id)  # Ensure the business category exists
        
        # Activate the business category
        business_category.is_active = 'Y'
        business_category.modified_by = modified_by
        business_category.modified_on = datetime.utcnow()

        self.db.commit()
        self.db.refresh(business_category)
        return business_category

    def deactivate_business_category(self, business_category_id: int, modified_by: int):
        """Deactivate a business category."""
        business_category = self.get_by_id(business_category_id)  # Ensure the business category exists
        
        # Deactivate the business category
        business_category.is_active = 'N'
        business_category.modified_by = modified_by
        business_category.modified_on = datetime.utcnow()

        self.db.commit()
        self.db.refresh(business_category)
        return business_category

    def get_active_business_categories(self):
        """Fetch all active business categories with business type names."""
        business_categories = self.db.query(
            BusinessCategory,
            BusinessType.type_name.label('business_type_name')
        ).join(
            BusinessType, 
            BusinessCategory.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessCategory.is_active == 'Y',
            BusinessCategory.is_deleted == 'N'
        ).all()
        
        if not business_categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active business categories found in the database."
            )
        
        # Convert to list of dictionaries with business type name
        result = []
        for category, business_type_name in business_categories:
            category_dict = {
                'business_category_id': category.business_category_id,
                'business_type_id': category.business_type_id,
                'business_type_name': business_type_name,
                'business_category_name': category.business_category_name,
                'business_category_short_name': category.business_category_short_name,
                'business_category_code': category.business_category_code,
                'is_active': category.is_active,
                'business_category_media': category.business_category_media,
                'icon': category.icon,
                'business_category_description': category.business_category_description,
                'added_by': category.added_by,
                'added_on': category.added_on,
                'modified_by': category.modified_by,
                'modified_on': category.modified_on,
                'is_deleted': category.is_deleted,
                'deleted_by': category.deleted_by,
                'deleted_on': category.deleted_on
            }
            result.append(category_dict)
        
        return result

    def get_inactive_business_categories(self):
        """Fetch all inactive business categories with business type names."""
        business_categories = self.db.query(
            BusinessCategory,
            BusinessType.type_name.label('business_type_name')
        ).join(
            BusinessType, 
            BusinessCategory.business_type_id == BusinessType.business_type_id
        ).filter(
            BusinessCategory.is_active == 'N',
            BusinessCategory.is_deleted == 'N'
        ).all()
        
        if not business_categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No inactive business categories found in the database."
            )
        
        # Convert to list of dictionaries with business type name
        result = []
        for category, business_type_name in business_categories:
            category_dict = {
                'business_category_id': category.business_category_id,
                'business_type_id': category.business_type_id,
                'business_type_name': business_type_name,
                'business_category_name': category.business_category_name,
                'business_category_short_name': category.business_category_short_name,
                'business_category_code': category.business_category_code,
                'is_active': category.is_active,
                'business_category_media': category.business_category_media,
                'icon': category.icon,
                'business_category_description': category.business_category_description,
                'added_by': category.added_by,
                'added_on': category.added_on,
                'modified_by': category.modified_by,
                'modified_on': category.modified_on,
                'is_deleted': category.is_deleted,
                'deleted_by': category.deleted_by,
                'deleted_on': category.deleted_on
            }
            result.append(category_dict)
        
        return result
