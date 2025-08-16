from fastapi import HTTPException, status
from app.repositories.UserModules.pages import PageRepository
from app.schemas.UserModules.pages import PageCreate, PageUpdate, PageResponse


class PageService:
    def __init__(self, page_repository: PageRepository, security_key: str):
        self.page_repository = page_repository
        self.security_key = security_key

    def get_all_pages(self, security_key: str):
        """Fetch all pages."""
        pages = self.page_repository.get_all_pages()
        return {
            "status": "success",
            "message": "Pages retrieved successfully.",
            "data": pages
        }

    def get_page_by_id(self, page_id: int, security_key: str):
        """Fetch a page by its ID."""
        page = self.page_repository.get_by_id(page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page with ID {page_id} not found."
            )
        return {
            "status": "success",
            "message": f"Page with ID {page_id} retrieved successfully.",
            "data": page
        }

    def create_page(self, page_data: PageCreate, security_key: str, added_by: int):
        """Create a new page."""
        # Check if a page with the same name already exists
        existing_page = self.page_repository.get_by_name(page_data.page_name)
        if existing_page:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Page with name '{page_data.page_name}' already exists."
            )

        # Create the new page
        new_page = self.page_repository.create_page(page_data, added_by)
        return {
            "status": "success",
            "message": "Page created successfully.",
            "data": new_page
        }

    def update_page(self, page_id: int, page_data: PageUpdate, security_key: str, modified_by: int):
        """Update an existing page."""
        # Ensure the page exists
        page = self.page_repository.get_by_id(page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page with ID {page_id} not found."
            )

        # Prevent updating to a duplicate name
        if page_data.page_name:
            existing_page = self.page_repository.get_by_name(page_data.page_name)
            if existing_page and existing_page.page_id != page_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Another page with name '{page_data.page_name}' already exists."
                )

        # Update the page
        updated_page = self.page_repository.update_page(page_id, page_data, modified_by)
        return {
            "status": "success",
            "message": f"Page with ID {page_id} updated successfully.",
            "data": updated_page
        }

    def delete_page(self, page_id: int, security_key: str, deleted_by: int):
        """Delete a page by its ID."""
        # Ensure the page exists
        page = self.page_repository.get_by_id(page_id)
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page with ID {page_id} not found."
            )

        # Perform the deletion
        result = self.page_repository.delete(page_id, deleted_by)
        return {
            "status": "success",
            "message": f"Page with ID {page_id} deleted successfully.",
            "data": result
        }

    def activate_page(self, page_id: int, security_key: str, modified_by: int):
        """Activate a page."""
        activated_page = self.page_repository.activate_page(page_id, modified_by)
        return {
            "status": "success",
            "message": f"Page with ID {page_id} activated successfully.",
            "data": activated_page
        }

    def deactivate_page(self, page_id: int, security_key: str, modified_by: int):
        """Deactivate a page."""
        deactivated_page = self.page_repository.deactivate_page(page_id, modified_by)
        return {
            "status": "success",
            "message": f"Page with ID {page_id} deactivated successfully.",
            "data": deactivated_page
        }

    def get_active_pages(self, security_key: str):
        """Get all active pages."""
        pages = self.page_repository.get_active_pages()
        return {
            "status": "success",
            "message": "Active pages retrieved successfully.",
            "data": pages
        }

    def get_inactive_pages(self, security_key: str):
        """Get all inactive pages."""
        pages = self.page_repository.get_inactive_pages()
        return {
            "status": "success",
            "message": "Inactive pages retrieved successfully.",
            "data": pages
        }