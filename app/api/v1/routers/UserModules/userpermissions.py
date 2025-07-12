from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.UserModules.userpermissions import UserPermissionCreate, UserPermissionUpdate
from app.services.UserModules.userpermissions import UserPermissionService
from app.repositories.UserModules.userpermissions import UserPermissionRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
SECURITY_KEY = os.getenv("SECRET_KEY")

router = APIRouter()


def validate_security_key(provided_key: str):
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )


@router.get("/all-userpermission", response_model=dict)
def get_all_user_permissions(
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    validate_security_key(security_key)
    service = UserPermissionService(UserPermissionRepository(db), SECURITY_KEY)
    user_permission = service.get_all_user_permission(security_key)
    return {
        "status": "success",
        "message": "User permissions retrieved successfully.",
        "data": user_permission["data"]
    }


@router.get("/get-by-userpermission/{user_permission_id}", response_model=dict)
def get_user_permission_by_id(
    user_permission_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    validate_security_key(security_key)
    service = UserPermissionService(UserPermissionRepository(db), SECURITY_KEY)
    user_permission = service.get_user_permission_by_id(user_permission_id, security_key)
    return {
        "status": "success",
        "message": f"User permission {user_permission_id} retrieved successfully.",
        "data": user_permission["data"]
    }


@router.post("/add-userpermission", response_model=dict, status_code=status.HTTP_201_CREATED)
def create_user_permission(
    user_permission: UserPermissionCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    validate_security_key(security_key)
    service = UserPermissionService(UserPermissionRepository(db), SECURITY_KEY)
    new_user_permission = service.create_user_permission(user_permission, security_key, added_by=1)
    return {
        "status": "success",
        "message": "User permission created successfully.",
        "data": new_user_permission["data"]
    }


@router.put("/update-userpermission/{user_permission_id}", response_model=dict)
def update_user_permission(
    user_permission_id: int,
    user_permission: UserPermissionUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    validate_security_key(security_key)
    service = UserPermissionService(UserPermissionRepository(db), SECURITY_KEY)
    updated_user_permission = service.update_user_permission(user_permission_id, user_permission, security_key, modified_by=1)
    return {
        "status": "success",
        "message": f"User permission {user_permission_id} updated successfully.",
        "data": updated_user_permission["data"]
    }


@router.delete("/delete-userpermission/{user_permission_id}", response_model=dict)
def delete_user_permission(
    user_permission_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)
):
    validate_security_key(security_key)
    service = UserPermissionService(UserPermissionRepository(db), SECURITY_KEY)
    service.delete_user_permission(user_permission_id, security_key, deleted_by=1)
    return {
        "status": "success",
        "message": f"User permission {user_permission_id} deleted successfully."
    }
