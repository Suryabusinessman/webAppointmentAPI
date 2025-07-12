from sqlalchemy.orm import Session
from app.models.BusinessModules.businessmanuser import BusinessmanUser
from app.schemas.BusinessModules.businessmanuser import BusinessmanUserCreate, BusinessmanUserUpdate
from fastapi import HTTPException, status
from datetime import datetime

class BusinessmanUserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active Business  users."""
        business_users = self.db.query(BusinessmanUser).filter(BusinessmanUser.Is_Deleted == 'N').all()
        if not business_users:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No business users found in the database."
            )
        return business_users

    def get_by_id(self, businessman_user_id: int):
        """Fetch a user by their ID."""
        user = self.db.query(BusinessmanUser).filter(
            BusinessmanUser.Businessman_User_Id == businessman_user_id,
            BusinessmanUser.Is_Deleted == 'N'
        ).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {businessman_user_id} not found."
            )
        return user

    # def get_by_email(self, email: str):
    #     """Fetch a user by their email."""
    #     user = self.db.query(BusinessmanUser).filter(
    #         BusinessmanUser.Email == email,
    #         BusinessmanUser.Is_Deleted == 'N'
    #     ).first()
    #     return user
    def get_by_user_and_bussienss_type(self, bussienss_type_id: int, user_id: int, user_type_id: int):
        """Check if a user permission exists for a given Page ID and User Type ID."""
        return self.db.query(BusinessmanUser).filter(
            BusinessmanUser.Business_Type_Id == bussienss_type_id,
            BusinessmanUser.User_Id == user_id,
            BusinessmanUser.User_Type_Id == user_type_id,
            BusinessmanUser.Is_Deleted == 'N'
        ).first()

    def create(self, business_man_user_data: BusinessmanUserCreate, added_by: int):
        """Create a new business type."""
        # Check if a business type with the same name already exists
        existing_business_man_user = self.db.query(BusinessmanUser).filter(
             BusinessmanUser.User_Id == business_man_user_data.User_Id,
            BusinessmanUser.Business_Type_Id == business_man_user_data.Business_Type_Id,
            BusinessmanUser.User_Type_Id == business_man_user_data.User_Type_Id,
            BusinessmanUser.Is_Deleted == 'N'
        ).first()

        # Log a message if the business type already exists
        if existing_business_man_user:
            print(f"Business Type with name already exists. Creating a new business type.")

        # Create the new business type regardless of whether the name exists
        new_business_type = BusinessmanUser(
            User_Id= business_man_user_data.User_Id,
            User_Type_Id= business_man_user_data.User_Type_Id,
            Business_Type_Id= business_man_user_data.Business_Type_Id,
            Brand_Name = business_man_user_data.Brand_Name,
            Business_Type_Name = business_man_user_data.Business_Type_Name,
            Is_Active = business_man_user_data.Is_Active,
            Business_Code = business_man_user_data.Business_Code,
            Business_Status = business_man_user_data.Business_Status,
            Bussiness_Logo = business_man_user_data.Bussiness_Logo,
            Bussiness_Banner = business_man_user_data.Bussiness_Banner,
            Bussiness_Description = business_man_user_data.Bussiness_Description,
            Is_Deleted='N',
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_business_type)
        self.db.commit()
        self.db.refresh(new_business_type)
        return new_business_type

    def update(self, business_man_user_id: int, business_man_user_data: BusinessmanUserUpdate, modified_by: int):
        """Update an existing business type."""

        business_man_user = self.get_by_id(business_man_user_id)  # Ensure the business type exists

        # Check if the new name already exists for another business type
        if business_man_user_data.User_Id and business_man_user_data.User_Type_Id and business_man_user_data.Business_Type_Id:
            new_user_id = business_man_user_data.User_Id if business_man_user_data.User_Id is not None else business_man_user.User_Id
            new_user_type_id = business_man_user_data.User_Type_Id if business_man_user_data.User_Type_Id is not None else business_man_user.User_Type_Id
            new_user_business_type_id = business_man_user_data.Business_Type_Id if business_man_user_data.Business_Type_Id is not None else business_man_user.Business_Type_Id

            duplicate = self.db.query(BusinessmanUser).filter(
                BusinessmanUser.User_Id == new_user_id,
                BusinessmanUser.User_Type_Id == new_user_type_id,
                BusinessmanUser.Business_Type_Id == new_user_business_type_id,
                BusinessmanUser.Businessman_User_Id != business_man_user_id,
                BusinessmanUser.Is_Deleted == 'N'
            ).first()

            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another User Permission with this Page ID and User Type ID already exists."
                )

            business_man_user.User_Id = new_user_id
            business_man_user.User_Type_Id = new_user_type_id
            business_man_user.Business_Type_Id = new_user_business_type_id

        # Update permission flags
        if business_man_user_data.Brand_Name:
            business_man_user.Brand_Name = business_man_user_data.Brand_Name
        if business_man_user_data.Business_Type_Name:
            business_man_user.Business_Type_Name = business_man_user_data.Business_Type_Name
        if business_man_user_data.Is_Active is not None:
            business_man_user.Is_Active = business_man_user_data.Is_Active
        if business_man_user_data.Business_Code:
            business_man_user.Business_Code = business_man_user_data.Business_Code
        if business_man_user_data.Business_Status:
            business_man_user.Business_Status = business_man_user_data.Business_Status
        if business_man_user_data.Bussiness_Logo:
            business_man_user.Bussiness_Logo = business_man_user_data.Bussiness_Logo
        if business_man_user_data.Bussiness_Banner:
            business_man_user.Bussiness_Banner = business_man_user_data.Bussiness_Banner
        if business_man_user_data.Bussiness_Description:
            business_man_user.Bussiness_Description = business_man_user_data.Bussiness_Description

        # Audit fields
        business_man_user.Modified_By = modified_by
        business_man_user.Modified_On = datetime.utcnow()

        self.db.commit()
        self.db.refresh(business_man_user)
        return business_man_user

    def delete(self, business_man_user_id: int, deleted_by: int):
        """Soft delete a business type by its ID."""
        business_man_user = self.get_by_id(business_man_user_id)  # Ensure the business type exists

        # Perform a soft delete
        business_man_user.Is_Deleted = 'Y'
        business_man_user.Deleted_By = deleted_by
        business_man_user.Deleted_On = datetime.utcnow()

        self.db.commit()
        return {"message": f"Business Type with ID {business_man_user_id} deleted successfully."}