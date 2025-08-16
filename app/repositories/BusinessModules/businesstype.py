from sqlalchemy.orm import Session
from app.models.BusinessModules.businesstype import BusinessType
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate, BusinessTypeResponse
from fastapi import HTTPException, status
from datetime import datetime


class BusinessTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active business types."""
        business_types = self.db.query(BusinessType).filter(BusinessType.is_active == 'Y').all()
        if not business_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Business types found in the database."
            )
        return business_types

    def get_by_id(self, business_type_id: int):
        """Fetch a business type by its ID."""
        business_type = self.db.query(BusinessType).filter(
            BusinessType.business_type_id == business_type_id,
            BusinessType.is_active == 'Y'
        ).first()
        if not business_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Type with ID {business_type_id} not found."
            )
        return business_type

    def get_by_name(self, business_type_name: str):
        """Fetch a business type by its name."""
        business_type = self.db.query(BusinessType).filter(
            BusinessType.type_name == business_type_name,
            BusinessType.is_active == 'Y'
        ).first()
        return business_type

    def create(self, business_type_data: BusinessTypeCreate, added_by: int):
        """Create a new business type."""
        # Check if a business type with the same name already exists
        existing_business_type = self.db.query(BusinessType).filter(
            BusinessType.type_name == business_type_data.type_name,
            BusinessType.is_active == 'Y'
        ).first()

        if existing_business_type:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Business Type with name '{business_type_data.type_name}' already exists."
            )

        # Create the new business type
        new_business_type = BusinessType(
            type_name=business_type_data.type_name,
            description=business_type_data.description,
            icon=business_type_data.icon,
            color=business_type_data.color,
            features=business_type_data.features,
            business_media=business_type_data.business_media,
            is_active=business_type_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self.db.add(new_business_type)
        self.db.commit()
        self.db.refresh(new_business_type)
        return new_business_type

    def update(self, business_type_id: int, business_type_data: BusinessTypeUpdate, modified_by: int):
        """Update an existing business type."""
        business_type = self.get_by_id(business_type_id)  # Ensure the business type exists

        # Check if the new name already exists for another business type
        if business_type_data.type_name:
            existing_business_type = self.db.query(BusinessType).filter(
                BusinessType.type_name == business_type_data.type_name,
                BusinessType.business_type_id != business_type_id,
                BusinessType.is_active == 'Y'
            ).first()
            if existing_business_type:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Business Type with name '{business_type_data.type_name}' already exists."
                )
            business_type.type_name = business_type_data.type_name

        # Update other fields if provided
        if business_type_data.description is not None:
            business_type.description = business_type_data.description
        if business_type_data.icon is not None:
            business_type.icon = business_type_data.icon
        if business_type_data.color is not None:
            business_type.color = business_type_data.color
        if business_type_data.features is not None:
            business_type.features = business_type_data.features
        if business_type_data.business_media is not None:
            business_type.business_media = business_type_data.business_media
        if business_type_data.is_active is not None:
            business_type.is_active = business_type_data.is_active

        # Update audit fields
        business_type.updated_at = datetime.utcnow()

        self.db.commit()
        self.db.refresh(business_type)
        return business_type

    def delete(self, business_type_id: int, deleted_by: int):
        """Soft delete a business type by its ID."""
        business_type = self.get_by_id(business_type_id)  # Ensure the business type exists

        # Perform a soft delete
        business_type.is_active = 'N'
        business_type.updated_at = datetime.utcnow()

        self.db.commit()
        return business_type

    def get_active_business_types(self):
        """Get all active business types."""
        return self.db.query(BusinessType).filter(BusinessType.is_active == 'Y').all()

    def get_inactive_business_types(self):
        """Get all inactive business types."""
        return self.db.query(BusinessType).filter(BusinessType.is_active == 'N').all()

    def activate_business_type(self, business_type_id: int, modified_by: int):
        """Activate a business type."""
        business_type = self.get_by_id(business_type_id)
        business_type.is_active = 'Y'
        business_type.updated_at = datetime.utcnow()
        self.db.commit()
        return business_type

    def deactivate_business_type(self, business_type_id: int, modified_by: int):
        """Deactivate a business type."""
        business_type = self.get_by_id(business_type_id)
        business_type.is_active = 'N'
        business_type.updated_at = datetime.utcnow()
        self.db.commit()
        return business_type