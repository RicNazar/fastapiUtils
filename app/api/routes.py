from fastapi import APIRouter
from app.api.excel.routes import router as excel_router

router = APIRouter()

router.include_router(excel_router, prefix="/excel", tags=["excel"])

@router.get("/",include_in_schema=False)
async def apis():
    return {"status": "Ok"}