from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from typing import List
from app.schemas.BusinessModules.businessmanuser import BusinessmanUserCreate, BusinessmanUserUpdate
from app.services.BusinessModules.businessmanuser import BusinessmanUserService
from app.repositories.BusinessModules.businessmanuser import BusinessmanUserRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os

load_dotenv()
SECURITY_KEY = os.getenv("SECRET_KEY")

router = APIRouter()

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )
    
def validate_security_key_new(secret_key: str = Header(..., alias="secret-key")):
    if secret_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )


@router.get("/all-businessmanusers", response_model=dict)
def get_all_businessman_users(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all business types.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)
    businessman_users = service.get_all_businessman_users(security_key)
    return {
        "status": "success",
        "message": "Businessman User retrieved successfully.",
        "data": businessman_users["data"]
    }

@router.get("/businessmanusers/{businessman_user_id}", response_model=dict)
def get_businessman_user(
    businessman_user_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a Businessman User by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)
    businessman_user = service.get_businessman_user_by_id(businessman_user_id, security_key)
    return {
        "status": "success",
        "message": f"Businessman User with ID {businessman_user_id} retrieved successfully.",
        "data": businessman_user["data"]
    }

@router.post("/add-businessmanusers", response_model=dict)
def create_businessman_user(
    businessman_user_data: BusinessmanUserCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # added_by: int = 1  # Assuming added_by is passed as a query parameter or header
):
    """
    Create a new Businessman User.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)
    businessman_user = service.create_businessman_user(businessman_user_data, security_key, added_by=1)  # Assuming added_by is 1 for this example
    if not businessman_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create Businessman User."
        )
    return {
        "status": "success",
        "message": "Business type created successfully.",
        "data": businessman_user["data"]
    }

@router.post("/add-multiplebusinessmanusers", response_model=dict)
def create_multiple_businessman_users(
    businessman_user_data: List[BusinessmanUserCreate],
    db: Session = Depends(get_db),
    security_key: str = Header(None),
):
    if not security_key:
        raise HTTPException(status_code=400, detail="Security key is required.")
    validate_security_key_new(security_key)

    service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)
    added_by = businessman_user_data[0].Added_By if businessman_user_data else 1
    result = service.create_multiple_businessman_users(businessman_user_data, security_key, added_by)

    return {
        "status": "success",
        "message": f"{len(result)} business records created.",
        "data": result,
    }
# def create_multiple_businessman_users(
#     businessman_users_data: List[BusinessmanUserCreate],
#     db: Session = Depends(get_db),
#     security_key: str = Header(None)
# ):
#     """
#     Create multiple Businessman Users.
#     """
#     if not security_key:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Security key is required."
#         )

#     validate_security_key(security_key)
#     service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)

#     created_users = []
#     for data in businessman_users_data:
#         result = service.create_multiple_businessman_users(data, security_key, added_by=1)
#         if result and result.get("data"):
#             created_users.append(result["data"])
#         else:
#             # Log failure but continue
#             continue

#     return {
#         "status": "success",
#         "message": f"{len(created_users)} business records created.",
#         "data": created_users
#     }

@router.put("/update-businessmanusers/{businessman_user_id}", response_model=dict)
def update_businessman_user(
    businessman_user_id: int,
    businessman_user_data: BusinessmanUserUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # updated_by: int = 1  # Assuming updated_by is passed as a query parameter or header
):
    """
    Update an existing Businessman User.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)
    businessman_user = service.update_businessman_user(businessman_user_id, businessman_user_data, security_key, updated_by=1)  # Assuming updated_by is 1 for this example
    if not businessman_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update Businessman User."
        )
    if not businessman_user["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Businessman User with ID {businessman_user_id} not found."
        )
    # Return the updated businessman user object
    return {
        "status": "success",
        "message": f"Businessman User with ID {businessman_user_id} updated successfully.",
        "data": businessman_user["data"]
    }

@router.delete("/delete-businessmanusers/{businessman_user_id}", response_model=dict)
def delete_businessman_user(
    businessman_user_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None),  # Accept security key in the request headers
    # deleted_by: int = 1  # Assuming deleted_by is passed as a query parameter or header
):
    """
    Delete a Businessman User by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessmanUserService(BusinessmanUserRepository(db), SECURITY_KEY)
    businessman_user = service.delete_businessman_user(businessman_user_id, security_key, deleted_by=1)  # Assuming deleted_by is 1 for this example
    if not businessman_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete Businessman User."
        )
    return {
        "status": "success",
        "message": f"Businessman User with ID {businessman_user_id} deleted successfully.",
        "data": businessman_user["data"]
    }

