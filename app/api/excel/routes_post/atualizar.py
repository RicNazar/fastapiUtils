from typing import Annotated,Any
from fastapi import APIRouter, Depends
from app.api.excel import dependencies as dp
from pydantic import BaseModel,Field

router = APIRouter()

class AtualizarRequest(BaseModel):
    tabela: Annotated[str, Field(description="Nome da tabela a ser atualizada",examples=["users"])]
    matriz: Annotated[list[list[Any]], Field(description="Matriz de dados a ser atualizada",examples=[[["id","name","MD"],[1,"John Doe","A"],[2,"Jane Doe","D"]]])]


@router.post("/")
async def atualizar(body: AtualizarRequest, excel: dp.Excel = Depends(dp.get_excel)):
    try:
        return excel.atualizar(
            tabela=body.tabela,
            matriz=body.matriz
        )
    except Exception as e:
        return {"error": str(e)}