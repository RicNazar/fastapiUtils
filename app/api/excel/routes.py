from fastapi import APIRouter
from app.api.excel.routes_get import obter_estrutura
from app.api.excel.routes_post import pesquisar

router = APIRouter()

#Rotas get
router.include_router(obter_estrutura.router, prefix="/obter_estrutura")

#Rotas post
router.include_router(pesquisar.router, prefix="/pesquisar")

@router.get("/",include_in_schema=False)
async def check():
    return {"status": "Ok"}