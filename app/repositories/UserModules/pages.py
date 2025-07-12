from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.UserModules.pages import Page
from app.schemas.UserModules.pages import PageCreate, PageUpdate
from datetime import datetime
import pytz  # For timezone handling


class PageRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------- Get All Pages ----------------------
    
    def get_all_pages(self):
        """Fetch all active pages."""
        pages = self.db.query(Page).filter(Page.Is_Deleted == 'N').all()
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pages found in the database."
            )
        return pages

    # ---------------------- Get Page by ID ----------------------

    def get_by_id(self, page_id: int):
        """Fetch a pages by its ID."""
        pages = self.db.query(Page).filter(
            Page.Page_Id == page_id,
            Page.Is_Deleted == 'N'
        ).first()
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"pages with ID {page_id} not found."
            )
        return pages
    
# ---------------------- Get by page name ----------------------
    def get_by_name(self, page_name: str):
        """Fetch a pages by its name."""
        pages = self.db.query(Page).filter(
            Page.Page_Name == page_name,
            Page.Is_Deleted == 'N'
        ).first()
        return pages
    # ---------------------- Create Page ----------------------

    def create_page(self, page_data: PageCreate, added_by: int):
        """Create a new pages."""
        # Check if a pages with the same name already exists
        existing_pages = self.db.query(Page).filter(
            Page.Page_Name == page_data.Page_Name,
            Page.Is_Deleted == 'N'
        ).first()

        # Log a message if the pages already exists
        if existing_pages:
            print(f"Pages with name '{page_data.Page_Name}' already exists. Creating a new pages.")

        # Create the new pages regardless of whether the name exists
        new_pages = Page(
            Page_Name=page_data.Page_Name,
            Page_Display_Text=page_data.Page_Display_Text,
            Page_Navigation_URL=page_data.Page_Navigation_URL,
            Page_Parent_Id=page_data.Page_Parent_Id,
            Is_Internal=page_data.Is_Internal,
            Is_Deleted='N',
            Added_By=added_by,
            Added_On=datetime.utcnow()
        )
        self.db.add(new_pages)
        self.db.commit()
        self.db.refresh(new_pages)
        return new_pages

    # ---------------------- Update Page ----------------------

    def update_page(self, page_id: int, page_data: PageUpdate, modified_by: int):
        """Update an existing pages."""
        pages = self.get_by_id(page_id)  # Ensure the pages exists

        # Check if the new name already exists for another pages
        if page_data.Page_Name:
            existing_user_type = self.db.query(Page).filter(
                Page.Page_Name == page_data.Page_Name,
                Page.Page_Id != page_id,
                Page.Is_Deleted == 'N'
            ).first()
            if existing_user_type:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User type with name '{page_data.Page_Name}' already exists."
                )
            pages.Page_Name = page_data.Page_Name

        # Update other fields if provided
        if page_data.Page_Display_Text:
            pages.Page_Display_Text = page_data.Page_Display_Text
        if page_data.Page_Navigation_URL:
            pages.Page_Navigation_URL = page_data.Page_Navigation_URL
        if page_data.Page_Parent_Id is not None:
            pages.Page_Parent_Id = page_data.Page_Parent_Id
        if page_data.Is_Internal is not None:
            pages.Is_Internal = page_data.Is_Internal

        # Update audit fields
        pages.Modified_By = modified_by
        pages.Modified_On = datetime.utcnow()

        self.db.commit()
        self.db.refresh(pages)
        return pages
    # ---------------------- Delete Page ----------------------

    def delete(self, page_id: int, deleted_by: int):
        """Soft delete a pages by its ID."""
        pages = self.get_by_id(page_id)  # Ensure the pages exists

        # Perform a soft delete
        pages.Is_Deleted = 'Y'
        pages.Deleted_By = deleted_by
        pages.Deleted_On = datetime.utcnow()

        self.db.commit()
        return {"message": f"Pages with ID {page_id} deleted successfully."}