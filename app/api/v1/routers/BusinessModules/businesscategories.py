from fastapi import APIRouter, HTTPException, Depends, status, Header
from sqlalchemy.orm import Session
from app.schemas.BusinessModules.businesscategories import BusinessCategoryCreate, BusinessCategoryUpdate
from app.services.BusinessModules.businesscategories import BusinessCategoryService
from app.repositories.BusinessModules.businesscategories import BusinessCategoryRepository
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
    
@router.get("/all-businesscategories", response_model=dict)
def get_all_business_categories(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all business categories.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessCategoryService(BusinessCategoryRepository(db), SECURITY_KEY)
    business_categories = service.get_all_business_categories(security_key)
    if not business_categories["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No business categories found."
        )
    return {
        "status": "success",
        "message": "Business categories retrieved successfully.",
        "data": business_categories["data"]
    }

@router.get("/businesscategories/{business_category_id}", response_model=dict)
def get_business_category(
    business_category_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a business category by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessCategoryService(BusinessCategoryRepository(db), SECURITY_KEY)
    business_category = service.get_business_category_by_id(business_category_id, security_key)
    if not business_category["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business category not found."
        )
    return {
        "status": "success",
        "message": "Business category retrieved successfully.",
        "data": business_category["data"]
    }

@router.post("/add-businesscategories", response_model=dict)
def create_business_category(
    business_category: BusinessCategoryCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Create a new business category.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessCategoryService(BusinessCategoryRepository(db), SECURITY_KEY)
    created_category = service.create_business_category(business_category, security_key,added_by=1)
    if not created_category["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create business category."
        )
    return {
        "status": "success",
        "message": "Business category created successfully.",
        "data": created_category["data"]
    }

@router.put("/update-businesscategories/{business_category_id}", response_model=dict)
def update_business_category(
    business_category_id: int,
    business_category: BusinessCategoryUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Update an existing business category.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessCategoryService(BusinessCategoryRepository(db), SECURITY_KEY)
    updated_category = service.update_business_category(business_category_id, business_category, security_key, modified_by=1)
    if not updated_category["data"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update business category."
        )
    return {
        "status": "success",
        "message": "Business category updated successfully.",
        "data": updated_category["data"]
    }

@router.delete("/delete-businesscategories/{business_category_id}", response_model=dict)
def delete_business_category(
    business_category_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Delete a business category by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = BusinessCategoryService(BusinessCategoryRepository(db), SECURITY_KEY)
    deleted_category = service.delete_business_category(business_category_id, security_key, deleted_by=1)
    if not deleted_category["data"]:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Business category not found."
        )
    return {
        "status": "success",
        "message": "Business category deleted successfully.",
        "data": deleted_category["data"]
    }