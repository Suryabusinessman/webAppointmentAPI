from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session
from app.schemas.UserModules.pages import PageCreate, PageUpdate
from app.services.UserModules.pages import PageService
from app.repositories.UserModules.pages import PageRepository
from app.core.database import get_db
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get the security key from the .env file
SECURITY_KEY = os.getenv("SECRET_KEY")

# Define the router
router = APIRouter()

# ---------------------- Utility Function ----------------------

def validate_security_key(provided_key: str):
    """Validate the security key for API access."""
    if provided_key != SECURITY_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid security key."
        )

# ---------------------- Get All Pages ----------------------

@router.get("/all-pages", response_model=dict)
def get_all_pages(
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch all pages.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = PageService(PageRepository(db), SECURITY_KEY)
    pages = service.get_all_pages(security_key)
    return {
        "status": "success",
        "message": "Pages retrieved successfully.",
        "data": pages["data"]
    }

# ---------------------- Get Page by ID ----------------------

@router.get("/pages/{page_id}", response_model=dict)
def get_page_by_id(
    page_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Fetch a page by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = PageService(PageRepository(db), SECURITY_KEY)
    page = service.get_page_by_id(page_id, security_key)
    return {
        "status": "success",
        "message": f"Page with ID {page_id} retrieved successfully.",
        "data": page["data"]
    }

# ---------------------- Create Page ----------------------

@router.post("/add-pages", response_model=dict)
def create_page(
    page_data: PageCreate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Create a new page.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = PageService(PageRepository(db), SECURITY_KEY)
    new_page = service.create_page(page_data, security_key, added_by=1)  # Replace `1` with the actual user ID
    return {
        "status": "success",
        "message": "Page created successfully.",
        "data": new_page
    }

# ---------------------- Update Page ----------------------

@router.put("/update-pages/{page_id}", response_model=dict)
def update_page(
    page_id: int,
    page_data: PageUpdate,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Update an existing page.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = PageService(PageRepository(db), SECURITY_KEY)
    updated_page = service.update_page(page_id, page_data, security_key, modified_by=1)  # Replace `1` with the actual user ID
    return {
        "status": "success",
        "message": f"Page with ID {page_id} updated successfully.",
        "data": updated_page
    }

# ---------------------- Delete Page ----------------------

@router.delete("/delete-pages/{page_id}", response_model=dict)
def delete_page(
    page_id: int,
    db: Session = Depends(get_db),
    security_key: str = Header(None)  # Accept security key in the request headers
):
    """
    Delete a page by its ID.
    """
    if not security_key:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Security key is required."
        )
    validate_security_key(security_key)
    service = PageService(PageRepository(db), SECURITY_KEY)
    result = service.delete_page(page_id, security_key, deleted_by=1)  # Replace `1` with the actual user ID
    return {
        "status": "success",
        "message": f"Page with ID {page_id} deleted successfully.",
        "data": result
    }
