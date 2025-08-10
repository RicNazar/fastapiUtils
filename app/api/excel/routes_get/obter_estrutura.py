import datetime
import json
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends
from app.api.excel import dependencies as dp

router = APIRouter()


@router.get("/")
async def obter_estrutura(tabelas: Annotated[str,"Tabelas separadas por ;"]="", excel: dp.Excel = Depends(dp.get_excel)):
    tabelas_ok = [tabela.strip() for tabela in tabelas.split(";") if tabela.strip()]
    try:
        if len(tabelas_ok) == 0:
            return excel.db.estrutura
        else:
            return excel.coletar_estrutura(tabelas_ok)
    except Exception as e:
        return {"error": str(e)}