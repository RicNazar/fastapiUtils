from fastapi import APIRouter

router = APIRouter()

@router.post("/pesquisar")
async def excel_root():
    return {"status": "Ok"}