from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.excel import dependencies as dp

router = APIRouter()

@router.post("/")
async def obter_estrutura(tabelas: Annotated[str,"Tabelas separadas por ;"], excel: dp.Excel = Depends(dp.get_excel)):
    tabelas_ok = [tabela.strip() for tabela in tabelas.split(";") if tabela.strip()]
    if len(tabelas_ok) == 0:
        return excel.db.estrutura
    else:
        return excel.coletar_estrutura(tabelas_ok)