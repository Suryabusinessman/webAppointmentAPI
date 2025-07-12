from sqlalchemy.orm import Session
from app.models.UserModules.userpermissions import UserPermission
from app.models.UserModules.pages import Page
from app.schemas.UserModules.userpermissions import UserPermissionCreate, UserPermissionUpdate
from fastapi import HTTPException, status
from datetime import datetime


class UserPermissionRepository:
    """Repository for user permissions."""
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        """Fetch all active user types."""
        user_permission = self.db.query(UserPermission).filter(UserPermission.Is_Deleted == 'N').all()
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No user types found in the database."
            )
        return user_permission

    def get_by_id(self, user_permission_id: int):
        """Fetch a User Permission by its ID."""
        user_permission = self.db.query(UserPermission).filter(
            UserPermission.User_Permission_Id == user_permission_id,
            UserPermission.Is_Deleted == 'N'
        ).first()
        if not user_permission:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User Permission with ID {user_permission_id} not found."
            )
        return user_permission

    # def get_by_name(self, user_type_name: str):
    #     """Fetch a User Permission by its name."""
    #     user_permission = self.db.query(UserPermission).filter(
    #         UserPermission.User_Type_Name == user_type_name,
    #         UserPermission.Is_Deleted == 'N'
    #     ).first()
    #     return user_permission
    def get_by_page_and_user_type(self, page_id: int, user_type_id: int):
        """Check if a user permission exists for a given Page ID and User Type ID."""
        return self.db.query(UserPermission).filter(
            UserPermission.Page_Id == page_id,
            UserPermission.User_Type_Id == user_type_id,
            UserPermission.Is_Deleted == 'N'
        ).first()
    def get_by_user_type(self, user_type_id: int):
        """Fetch all User Permissions for a given User Type ID."""
        user_permissions = self.db.query(UserPermission).filter(
            UserPermission.User_Type_Id == user_type_id,
            UserPermission.Is_Deleted == 'N'
        ).all()
        # if not user_permissions:
        #     raise HTTPException(
        #         status_code=status.HTTP_404_NOT_FOUND,
        #         detail=f"No permissions found for User Type ID {user_type_id}."
        #     )
        return user_permissions
    def get_user_permissions_with_pages(self, user_type_id: int):
        """Fetch all User Permissions with their corresponding Page names for a given User Type ID."""
        permissions = self.db.query(UserPermission, Page).join(
            Page, UserPermission.Page_Id == Page.Page_Id
        ).filter(
            UserPermission.User_Type_Id == user_type_id,
            UserPermission.Is_Deleted == 'N',
            Page.Is_Deleted == 'N'
        ).all()

        result = []
        for permission, page in permissions:
            result.append({
                "User_Permission_Id": permission.User_Permission_Id,
                "User_Type_Id": permission.User_Type_Id,
                "Page_Id": page.Page_Id,
                "Page_Name": page.Page_Name,
                "Page_Display_Text": page.Page_Display_Text,
                "Page_Navigation_URL": page.Page_Navigation_URL,
                "Page_Parent_Id": page.Page_Parent_Id,
                "Is_Internal": page.Is_Internal,
                "Can_View": permission.Can_View,
                "Can_Create": permission.Can_Create,
                "Can_Update": permission.Can_Update,
                "Can_Delete": permission.Can_Delete,
            })

        return result
    def create(self, user_permission_data: UserPermissionCreate, added_by: int):
        """Create a new User Permission."""
        # Check if a UserPermission with the same Page_Id and User_Type_Id already exists
        existing_permission = self.db.query(UserPermission).filter(
            UserPermission.Page_Id == user_permission_data.Page_Id,
            UserPermission.User_Type_Id == user_permission_data.User_Type_Id,
            UserPermission.Is_Deleted == 'N'
        ).first()

        if existing_permission:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A User Permission with this Page ID and User Type ID already exists."
            )

        new_user_permission = UserPermission(
            User_Type_Id=user_permission_data.User_Type_Id,
            Page_Id=user_permission_data.Page_Id,
            Can_View=user_permission_data.Can_View,
            Can_Create=user_permission_data.Can_Create,
            Can_Update=user_permission_data.Can_Update,
            Can_Delete=user_permission_data.Can_Delete,
            Is_Deleted='N',
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_user_permission)
        self.db.commit()
        self.db.refresh(new_user_permission)
        return new_user_permission


    def update(self, user_permission_id: int, user_permission_data: UserPermissionUpdate, modified_by: int):
        """Update an existing User Permission."""
        user_permission = self.get_by_id(user_permission_id)  # Ensure it exists

        # Check for duplicate if Page_Id or User_Type_Id are changing
        if user_permission_data.Page_Id and user_permission_data.User_Type_Id:
            new_page_id = user_permission_data.Page_Id if user_permission_data.Page_Id is not None else user_permission.Page_Id
            new_user_type_id = user_permission_data.User_Type_Id if user_permission_data.User_Type_Id is not None else user_permission.User_Type_Id

            duplicate = self.db.query(UserPermission).filter(
                UserPermission.Page_Id == new_page_id,
                UserPermission.User_Type_Id == new_user_type_id,
                UserPermission.User_Permission_Id != user_permission_id,
                UserPermission.Is_Deleted == 'N'
            ).first()

            if duplicate:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Another User Permission with this Page ID and User Type ID already exists."
                )

            user_permission.Page_Id = new_page_id
            user_permission.User_Type_Id = new_user_type_id

        # Update permission flags
        if user_permission_data.Can_View is not None:
            user_permission.Can_View = user_permission_data.Can_View
        if user_permission_data.Can_Create is not None:
            user_permission.Can_Create = user_permission_data.Can_Create
        if user_permission_data.Can_Update is not None:
            user_permission.Can_Update = user_permission_data.Can_Update
        if user_permission_data.Can_Delete is not None:
            user_permission.Can_Delete = user_permission_data.Can_Delete

        # Audit fields
        user_permission.Modified_By = modified_by
        user_permission.Modified_On = datetime.utcnow()

        self.db.commit()
        self.db.refresh(user_permission)
        return user_permission


    def delete(self, user_permission_id: int, deleted_by: int):
        """Soft delete a User Permission by its ID."""
        user_permission = self.get_by_id(user_permission_id)  # Ensure the User Permission exists

        # Perform a soft delete
        user_permission.Is_Deleted = 'Y'
        user_permission.Deleted_By = deleted_by
        user_permission.Deleted_On = datetime.utcnow()

        self.db.commit()
        return {"message": f"User Permission with ID {user_permission_id} deleted successfully."}