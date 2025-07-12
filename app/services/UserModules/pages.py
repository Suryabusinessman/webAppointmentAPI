from fastapi import HTTPException, status
from app.repositories.UserModules.pages import PageRepository
from app.schemas.UserModules.pages import PageCreate, PageUpdate


class PageService:
    def __init__(self, page_repository: PageRepository, security_key: str):
        self.page_repository = page_repository
        self.security_key = security_key

    def validate_security_key(self, provided_key: str):
        """Validate the security key for API access."""
        if provided_key != self.security_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid security key."
            )

    def get_all_pages(self, security_key: str):
        """Fetch all user types."""
        self.validate_security_key(security_key)
        pages = self.page_repository.get_all_pages()
        return {
            "status": "success",
            "message": "User types retrieved successfully.",
            "data": pages
        }


    def get_page_by_id(self, page_id: int, security_key: str):
        """Fetch a pages by its ID."""
        self.validate_security_key(security_key)
        pages = self.page_repository.get_by_id(page_id)
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User type with ID {page_id} not found."
            )
        return {
            "status": "success",
            "message": f"User type with ID {page_id} retrieved successfully.",
            "data": pages
        }



    def create_page(self, page_data: PageCreate, security_key: str, added_by: int):
        """Create a new pages."""
        self.validate_security_key(security_key)

        # Check if a pages with the same name already exists
        existing_pages = self.page_repository.get_by_name(page_data.Page_Name)
        if existing_pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Pages with name '{page_data.Page_Name}' already exists."
            )

        # Create the new pages
        new_pages = self.page_repository.create_page(page_data, added_by)
        return {
            "status": "success",
            "message": "pages created successfully.",
            "data": new_pages
        }


    def update_page(self, page_id: int, page_data: PageUpdate, security_key: str, modified_by: int):
        """Update an existing pages."""
        self.validate_security_key(security_key)

        # Ensure the pages exists
        pages = self.page_repository.get_by_id(page_id)
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pages with ID {page_id} not found."
            )

        # Prevent updating to a duplicate name
        if page_data.Page_Name:
            existing_pages = self.page_repository.get_by_name(page_data.Page_Name)
            if existing_pages and existing_pages.Page_Id != page_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Another Pages with name '{page_data.Page_Name}' already exists."
                )

        # Update the pages
        updated_pages = self.page_repository.update_page(page_id, page_data, modified_by)
        return {
            "status": "success",
            "message": f"Pages with ID {page_id} updated successfully.",
            "data": updated_pages
        }


    def delete_page(self, page_id: int, security_key: str, deleted_by: int):
        """Delete a pages by its ID."""
        self.validate_security_key(security_key)

        # Ensure the pages exists
        pages = self.page_repository.get_by_id(page_id)
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Pages with ID {page_id} not found."
            )

        # Perform the deletion
        result = self.page_repository.delete(page_id, deleted_by)
        return {
            "status": "success",
            "message": f"Pages with ID {page_id} deleted successfully.",
            "data": result
        }