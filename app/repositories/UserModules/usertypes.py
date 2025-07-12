from sqlalchemy.orm import Session
from app.models.UserModules.usertypes import UserType
from app.schemas.UserModules.usertypes import UserTypeCreate, UserTypeUpdate
from fastapi import HTTPException, status
from datetime import datetime


class UserTypeRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active user types."""
        user_types = self.db.query(UserType).filter(UserType.Is_Deleted == 'N').all()
        if not user_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user types found in the database."
            )
        return user_types

    def get_by_id(self, user_type_id: int):
        """Fetch a user type by its ID."""
        user_type = self.db.query(UserType).filter(
            UserType.User_Type_Id == user_type_id,
            UserType.Is_Deleted == 'N'
        ).first()
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )
        return user_type

    def get_by_name(self, user_type_name: str):
        """Fetch a user type by its name."""
        user_type = self.db.query(UserType).filter(
            UserType.User_Type_Name == user_type_name,
            UserType.Is_Deleted == 'N'
        ).first()
        # if not user_type:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"User type with name {user_type_name} not found."
        #     )
        return user_type

    def create(self, user_type_data: UserTypeCreate, added_by: int):
        """Create a new user type."""
        # Check if a user type with the same name already exists
        existing_user_type = self.db.query(UserType).filter(
            UserType.User_Type_Name == user_type_data.User_Type_Name,
            UserType.Is_Deleted == 'N'
        ).first()

        # Log a message if the user type already exists
        if existing_user_type:
            print(f"User type with name '{user_type_data.User_Type_Name}' already exists. Creating a new user type.")

        # Create the new user type regardless of whether the name exists
        new_user_type = UserType(
            User_Type_Name=user_type_data.User_Type_Name,
            User_Type_Desc=user_type_data.User_Type_Desc,
            Default_Page=user_type_data.Default_Page,
            Is_Member=user_type_data.Is_Member,
            Is_Active=user_type_data.Is_Active,
            Is_Deleted='N',
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_user_type)
        self.db.commit()
        self.db.refresh(new_user_type)
        return new_user_type

    def update(self, user_type_id: int, user_type_data: UserTypeUpdate, modified_by: int):
        """Update an existing user type."""
        user_type = self.get_by_id(user_type_id)  # Ensure the user type exists

        # Check if the new name already exists for another user type
        if user_type_data.User_Type_Name:
            existing_user_type = self.db.query(UserType).filter(
                UserType.User_Type_Name == user_type_data.User_Type_Name,
                UserType.User_Type_Id != user_type_id,
                UserType.Is_Deleted == 'N'
            ).first()
            if existing_user_type:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User type with name '{user_type_data.User_Type_Name}' already exists."
                )
            user_type.User_Type_Name = user_type_data.User_Type_Name

        # Update other fields if provided
        if user_type_data.User_Type_Desc:
            user_type.User_Type_Desc = user_type_data.User_Type_Desc
        if user_type_data.Default_Page:
            user_type.Default_Page = user_type_data.Default_Page
        if user_type_data.Is_Member is not None:
            user_type.Is_Member = user_type_data.Is_Member
        if user_type_data.Is_Active is not None:
            user_type.Is_Active = user_type_data.Is_Active

        # Update audit fields
        user_type.Modified_By = modified_by
        user_type.Modified_On = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user_type)
        return user_type

    def delete(self, user_type_id: int, deleted_by: int):
        """Soft delete a user type by its ID."""
        user_type = self.get_by_id(user_type_id)  # Ensure the user type exists

        # Perform a soft delete
        user_type.Is_Deleted = 'Y'
        user_type.Deleted_By = deleted_by
        user_type.Deleted_On = datetime.utcnow()

        self.db.commit()
        return {"status": "success","color":"success","message": f"User type with ID {user_type_id} deleted successfully."}