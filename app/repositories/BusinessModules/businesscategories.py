from sqlalchemy.orm import Session
from app.models.BusinessModules.businesscategory import BusinessCategory
from app.schemas.BusinessModules.businesscategories import BusinessCategoryCreate, BusinessCategoryUpdate
from fastapi import HTTPException, status
from datetime import datetime

class BusinessCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active business categories."""
        business_categories = self.db.query(BusinessCategory).filter(BusinessCategory.Is_Deleted == 'N').all()
        if not business_categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No Business categories found in the database."
            )
        return business_categories

    def get_by_id(self, business_category_id: int):
        """Fetch a business category by its ID."""
        business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.Business_Category_Id == business_category_id,
            BusinessCategory.Is_Deleted == 'N'
        ).first()
        if not business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )
        return business_category
    def get_by_name(self, business_category_name: str):
        """Fetch a business category by its name."""
        business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.Business_Category_Name == business_category_name,
            BusinessCategory.Is_Deleted == 'N'
        ).first()
        return business_category
    def create(self, business_category_data: BusinessCategoryCreate, added_by: int):
        """Create a new business category."""
        # Check if a business category with the same name already exists
        existing_business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.Business_Category_Name == business_category_data.Business_Category_Name,
            BusinessCategory.Is_Deleted == 'N'
        ).first()

        # Log a message if the business category already exists
        if existing_business_category:
            print(f"Business Category with name '{business_category_data.Business_Category_Name}' already exists. Creating a new business category.")

        # Create the new business category regardless of whether the name exists
        new_business_category = BusinessCategory(
            Business_Type_Id=business_category_data.Business_Type_Id,
            Business_Category_Name=business_category_data.Business_Category_Name,
            Business_Category_Short_Name=business_category_data.Business_Category_Short_Name,
            Business_Category_Code=business_category_data.Business_Category_Code,
            Is_Active=business_category_data.Is_Active,
            Business_Category_Media=business_category_data.Business_Category_Media,
            Business_Category_Description=business_category_data.Business_Category_Description,
            Added_By=added_by,
            Added_On=datetime.now(),
            Is_Deleted='N'
        )
        self.db.add(new_business_category)
        self.db.commit()
        self.db.refresh(new_business_category)
        return new_business_category
    def update(self, business_category_id: int, business_category_data: BusinessCategoryUpdate, modified_by: int):
        """Update an existing business category."""
        business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.Business_Category_Id == business_category_id,
            BusinessCategory.Is_Deleted == 'N'
        ).first()

        if not business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )

        # Update the fields of the business category
        for key, value in business_category_data.dict(exclude_unset=True).items():
            setattr(business_category, key, value)

        # Set the modified fields
        business_category.Modified_By = modified_by
        business_category.Modified_On = datetime.now()

        self.db.commit()
        self.db.refresh(business_category)
        return business_category
    def delete(self, business_category_id: int, deleted_by: int):
        """Soft delete a business category."""
        business_category = self.db.query(BusinessCategory).filter(
            BusinessCategory.Business_Category_Id == business_category_id,
            BusinessCategory.Is_Deleted == 'N'
        ).first()

        if not business_category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Business Category with ID {business_category_id} not found."
            )

        # Soft delete the business category
        business_category.Is_Deleted = 'Y'
        business_category.Deleted_By = deleted_by
        business_category.Deleted_On = datetime.now()

        self.db.commit()
        return {"message": "Business Category deleted successfully."}
