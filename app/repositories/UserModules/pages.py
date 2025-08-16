from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
from app.models.UserModules.pages import Page
from app.schemas.UserModules.pages import PageCreate, PageUpdate, PageResponse
from datetime import datetime
import pytz  # For timezone handling


class PageRepository:
    def __init__(self, db: Session):
        self.db = db

    # ---------------------- Get All Pages ----------------------
    
    def get_all_pages(self):
        """Fetch all active pages."""
        pages = self.db.query(Page).filter(Page.is_deleted == 'N').all()
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No pages found in the database."
            )
        return pages

    # ---------------------- Get Page by ID ----------------------

    def get_by_id(self, page_id: int):
        """Fetch a page by its ID."""
        page = self.db.query(Page).filter(
            Page.page_id == page_id,
            Page.is_deleted == 'N'
        ).first()
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page with ID {page_id} not found."
            )
        return page
    
    # ---------------------- Get by page name ----------------------
    def get_by_name(self, page_name: str):
        """Fetch a page by its name."""
        page = self.db.query(Page).filter(
            Page.page_name == page_name,
            Page.is_deleted == 'N'
        ).first()
        return page

    # ---------------------- Create Page ----------------------

    def create_page(self, page_data: PageCreate, added_by: int):
        """Create a new page."""
        # Check if a page with the same name already exists
        existing_page = self.db.query(Page).filter(
            Page.page_name == page_data.page_name,
            Page.is_deleted == 'N'
        ).first()

        # Log a message if the page already exists
        if existing_page:
            print(f"Page with name '{page_data.page_name}' already exists. Creating a new page.")

        # Create the new page regardless of whether the name exists
        new_page = Page(
            page_name=page_data.page_name,
            page_display_text=page_data.page_display_text,
            page_navigation_url=page_data.page_navigation_url,
            page_parent_id=page_data.page_parent_id,
            is_internal=page_data.is_internal,
            is_deleted='N',
            added_by=added_by,
            added_on=datetime.utcnow()
        )
        self.db.add(new_page)
        self.db.commit()
        self.db.refresh(new_page)
        return new_page

    # ---------------------- Update Page ----------------------

    def update_page(self, page_id: int, page_data: PageUpdate, modified_by: int):
        """Update an existing page."""
        page = self.get_by_id(page_id)  # Ensure the page exists

        # Check if the new name already exists for another page
        if page_data.page_name:
            existing_page = self.db.query(Page).filter(
                Page.page_name == page_data.page_name,
                Page.page_id != page_id,
                Page.is_deleted == 'N'
            ).first()
            if existing_page:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Page with name '{page_data.page_name}' already exists."
                )
            page.page_name = page_data.page_name

        # Update other fields if provided
        if page_data.page_display_text:
            page.page_display_text = page_data.page_display_text
        if page_data.page_navigation_url:
            page.page_navigation_url = page_data.page_navigation_url
        if page_data.page_parent_id is not None:
            page.page_parent_id = page_data.page_parent_id
        if page_data.is_internal is not None:
            page.is_internal = page_data.is_internal

        # Update audit fields
        page.modified_by = modified_by
        page.modified_on = datetime.utcnow()

        self.db.commit()
        self.db.refresh(page)
        return page

    # ---------------------- Delete Page ----------------------

    def delete(self, page_id: int, deleted_by: int):
        """Soft delete a page by its ID."""
        page = self.get_by_id(page_id)  # Ensure the page exists

        # Perform a soft delete
        page.is_deleted = 'Y'
        page.deleted_by = deleted_by
        page.deleted_on = datetime.utcnow()

        self.db.commit()
        return page

    # ---------------------- Additional Methods ----------------------

    def get_active_pages(self):
        """Get all active pages."""
        return self.db.query(Page).filter(Page.is_deleted == 'N').all()

    def get_inactive_pages(self):
        """Get all inactive pages."""
        return self.db.query(Page).filter(Page.is_deleted == 'Y').all()

    def activate_page(self, page_id: int, modified_by: int):
        """Activate a page."""
        page = self.get_by_id(page_id)
        page.is_deleted = 'N'
        page.modified_by = modified_by
        page.modified_on = datetime.utcnow()
        self.db.commit()
        return page

    def deactivate_page(self, page_id: int, modified_by: int):
        """Deactivate a page."""
        page = self.get_by_id(page_id)
        page.is_deleted = 'Y'
        page.modified_by = modified_by
        page.modified_on = datetime.utcnow()
        self.db.commit()
        return page