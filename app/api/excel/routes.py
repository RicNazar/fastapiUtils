from fastapi import APIRouter
from app.api.excel.routes_get import obter_estrutura,obter_cabecalhos,caregar_exemplo
from app.api.excel.routes_post import pesquisar,atualizar

router = APIRouter()

#Rotas get
router.include_router(caregar_exemplo.router, prefix="/carregar_exemplo")
router.include_router(obter_estrutura.router, prefix="/obter_estrutura")
router.include_router(obter_cabecalhos.router, prefix="/obter_cabecalhos")

#Rotas post
router.include_router(pesquisar.router, prefix="/pesquisar")
router.include_router(atualizar.router, prefix="/atualizar")

@router.get("/",include_in_schema=False)
async def check():
    return {"status": "Ok"}