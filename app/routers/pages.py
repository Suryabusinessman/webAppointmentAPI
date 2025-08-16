from fastapi import APIRouter, HTTPException
from app.schemas.pages import PageCreate, PageUpdate, Page
from app.repositories.pages import PageRepository

router = APIRouter()
page_repository = PageRepository()

@router.post("/", response_model=Page)
async def create_page(page: PageCreate):
    return await page_repository.create(page)

@router.get("/{page_id}", response_model=Page)
async def read_page(page_id: int):
    page = await page_repository.get(page_id)
    if not page:
        raise HTTPException(status_code=404, detail="Page not found")
    return page

@router.put("/{page_id}", response_model=Page)
async def update_page(page_id: int, page: PageUpdate):
    updated_page = await page_repository.update(page_id, page)
    if not updated_page:
        raise HTTPException(status_code=404, detail="Page not found")
    return updated_page

@router.delete("/{page_id}", response_model=dict)
async def delete_page(page_id: int):
    success = await page_repository.delete(page_id)
    if not success:
        raise HTTPException(status_code=404, detail="Page not found")
    return {"detail": "Page deleted successfully"}