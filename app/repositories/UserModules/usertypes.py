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
        user_types = self.db.query(UserType).filter(UserType.is_active == 'Y').all()
        if not user_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user types found in the database."
            )
        return user_types

    def get_by_id(self, user_type_id: int):
        """Fetch a user type by its ID (regardless of active status)."""
        user_type = self.db.query(UserType).filter(
            UserType.user_type_id == user_type_id
        ).first()
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )
        return user_type

    def get_active_by_id(self, user_type_id: int):
        """Fetch an active user type by its ID."""
        user_type = self.db.query(UserType).filter(
            UserType.user_type_id == user_type_id,
            UserType.is_active == 'Y'
        ).first()
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active user type with ID {user_type_id} not found."
            )
        return user_type

    def get_by_name(self, user_type_name: str):
        """Fetch a user type by its name."""
        user_type = self.db.query(UserType).filter(
            UserType.type_name == user_type_name,
            UserType.is_active == 'Y'
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
            UserType.type_name == user_type_data.type_name,
            UserType.is_active == 'Y'
        ).first()

        # Log a message if the user type already exists
        if existing_user_type:
            print(f"User type with name '{user_type_data.type_name}' already exists. Creating a new user type.")

        # Create the new user type regardless of whether the name exists
        new_user_type = UserType(
            type_name=user_type_data.type_name,
            description=user_type_data.description,
            default_page=user_type_data.default_page,
            permissions=user_type_data.permissions,
            is_active=user_type_data.is_active
        )
        self.db.add(new_user_type)
        self.db.commit()
        self.db.refresh(new_user_type)
        return new_user_type

    def update(self, user_type_id: int, user_type_data: UserTypeUpdate, modified_by: int):
        """Update an existing user type."""
        user_type = self.get_by_id(user_type_id)  # Ensure the user type exists

        # Check if the new name already exists for another user type
        if user_type_data.type_name:
            existing_user_type = self.db.query(UserType).filter(
                UserType.type_name == user_type_data.type_name,
                UserType.user_type_id != user_type_id,
                UserType.is_active == 'Y'
            ).first()
            if existing_user_type:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User type with name '{user_type_data.type_name}' already exists."
                )
            user_type.type_name = user_type_data.type_name

        # Update other fields if provided
        if user_type_data.description:
            user_type.description = user_type_data.description
        if user_type_data.default_page:
            user_type.default_page = user_type_data.default_page
        if user_type_data.permissions:
            user_type.permissions = user_type_data.permissions
        if user_type_data.is_active:
            user_type.is_active = user_type_data.is_active

        self.db.commit()
        self.db.refresh(user_type)
        return user_type

    def delete(self, user_type_id: int, deleted_by: int):
        """Delete a user type by its ID."""
        user_type = self.get_by_id(user_type_id)  # Ensure the user type exists

        # Soft delete the user type by setting is_active to 'N'
        user_type.is_active = 'N'

        self.db.commit()
        self.db.refresh(user_type)
        return user_type

    def activate(self, user_type_id: int):
        """Activate a user type by setting is_active to 'Y'."""
        user_type = self.db.query(UserType).filter(
            UserType.user_type_id == user_type_id
        ).first()
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )
        
        user_type.is_active = 'Y'
        self.db.commit()
        self.db.refresh(user_type)
        return user_type

    def deactivate(self, user_type_id: int):
        """Deactivate a user type by setting is_active to 'N'."""
        user_type = self.db.query(UserType).filter(
            UserType.user_type_id == user_type_id
        ).first()
        if not user_type:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {user_type_id} not found."
            )
        
        user_type.is_active = 'N'
        self.db.commit()
        self.db.refresh(user_type)
        return user_type

    def get_active(self):
        """Fetch all active user types."""
        user_types = self.db.query(UserType).filter(UserType.is_active == 'Y').all()
        if not user_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No active user types found in the database."
            )
        return user_types

    def get_inactive(self):
        """Fetch all inactive user types."""
        user_types = self.db.query(UserType).filter(UserType.is_active == 'N').all()
        if not user_types:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No inactive user types found in the database."
            )
        return user_types