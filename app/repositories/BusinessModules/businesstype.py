from sqlalchemy.orm import Session
from app.models.BusinessModules.businesstype import BusinessType
from app.schemas.BusinessModules.businesstype import BusinessTypeCreate, BusinessTypeUpdate
from fastapi import HTTPException, status
from datetime import datetime


class BusinessTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active user types."""
        business_types = self.db.query(BusinessType).filter(BusinessType.Is_Deleted == 'N').all()
        if not business_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Business types found in the database."
            )
        return business_types

    def get_by_id(self, business_type_id: int):
        """Fetch a business type by its ID."""
        business_type = self.db.query(BusinessType).filter(
            BusinessType.Business_Type_Id == business_type_id,
            BusinessType.Is_Deleted == 'N'
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
            BusinessType.Business_Type_Name == business_type_name,
            BusinessType.Is_Deleted == 'N'
        ).first()
        return business_type

    def create(self, business_type_data: BusinessTypeCreate, added_by: int):
        """Create a new business type."""
        # Check if a business type with the same name already exists
        existing_business_type = self.db.query(BusinessType).filter(
            BusinessType.Business_Type_Name == business_type_data.Business_Type_Name,
            BusinessType.Is_Deleted == 'N'
        ).first()

        # Log a message if the business type already exists
        if existing_business_type:
            print(f"Business Type with name '{business_type_data.Business_Type_Name}' already exists. Creating a new business type.")

        # Create the new business type regardless of whether the name exists
        new_business_type = BusinessType(
            Business_Type_Name=business_type_data.Business_Type_Name,
            Business_Type_Desc=business_type_data.Business_Type_Desc,
            Business_Code=business_type_data.Business_Code,
            Business_Status=business_type_data.Business_Status,
            Is_Active=business_type_data.Is_Active,
            Business_Media=business_type_data.Business_Media,
            Is_Deleted='N',
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_business_type)
        self.db.commit()
        self.db.refresh(new_business_type)
        return new_business_type

    def update(self, business_type_id: int, business_type_data: BusinessTypeUpdate, modified_by: int):
        """Update an existing business type."""
        business_type = self.get_by_id(business_type_id)  # Ensure the business type exists

        # Check if the new name already exists for another business type
        if business_type_data.Business_Type_Name:
            existing_business_type = self.db.query(BusinessType).filter(
                BusinessType.Business_Type_Name == business_type_data.Business_Type_Name,
                BusinessType.Business_Type_Id != business_type_id,
                BusinessType.Is_Deleted == 'N'
            ).first()
            if existing_business_type:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Business Type with name '{business_type_data.Business_Type_Name}' already exists."
                )
            business_type.Business_Type_Name = business_type_data.Business_Type_Name

        # Update other fields if provided
        if business_type_data.Business_Type_Desc:
            business_type.Business_Type_Desc = business_type_data.Business_Type_Desc
        if business_type_data.Business_Code:
            business_type.Business_Code = business_type_data.Business_Code
        if business_type_data.Business_Status:
            business_type.Business_Status = business_type_data.Business_Status
        if business_type_data.Is_Active is not None:
            business_type.Is_Active = business_type_data.Is_Active
        if business_type_data.Business_Media:
            business_type.Business_Media = business_type_data.Business_Media

        # Update audit fields
        business_type.Modified_By = modified_by
        business_type.Modified_On = datetime.utcnow()

        self.db.commit()
        self.db.refresh(business_type)
        return business_type

    def delete(self, business_type_id: int, deleted_by: int):
        """Soft delete a business type by its ID."""
        business_type = self.get_by_id(business_type_id)  # Ensure the business type exists

        # Perform a soft delete
        business_type.Is_Deleted = 'Y'
        business_type.Deleted_By = deleted_by
        business_type.Deleted_On = datetime.utcnow()

        self.db.commit()
        return {"message": f"Business Type with ID {business_type_id} deleted successfully."}