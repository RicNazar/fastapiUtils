from fastapi import APIRouter
from app.api.excel.routes_post import router as excel_router

router = APIRouter()

router.include_router(excel_router, prefix="/excel", tags=["excel"])

@router.get("/")
async def apis():
    return {"status": "Ok"}