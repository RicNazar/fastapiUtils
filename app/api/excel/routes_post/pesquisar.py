from typing import Annotated
from fastapi import APIRouter, Depends
from app.api.excel import dependencies as dp
from pydantic import BaseModel,Field

router = APIRouter()

class PesquisarRequest(BaseModel):
    colunas: Annotated[list[list[str]], Field(description="Colunas a serem pesquisadas",
                                              examples='[["id","idade","nome","telefone"]]' )]
    tabelas: Annotated[list[list[str]], Field(description="Tabelas onde a pesquisa será realizada",
                                              examples='[["pessoas","pessoas","pessoas","pessoas"]]')]
    criterios: Annotated[list[list[str]], Field(default=None,
                                                description="Critérios de pesquisa, primeira linha o cabeçalho, as demais os critérios",
                                                examples='[["uf","idade","idade","idade"],["SP",">30","<=40","<>10"],["PR","","",""]]' )]
    criterios_tabelas: Annotated[list[str]|None, Field(default=None,
                                                description="Tabelas relacionadas aos critérios",
                                                examples='[["pessoas","pessoas","pessoas","pessoas"]]' )]
    relacoes: Annotated[list[list[str]], Field(default=None,
                                              description="Relações entre as tabelas, 4 ou 5 colunas: tabela A, tabela B, Coluna tabela A, Coluna Tabela B, Relação(inner, left, right): Opcional padrão inner",
                                              examples='[["pessoas","pessoas","id","id","inner"],["pessoas","pessoas","id","id","inner"]]' )]
    caractere_especial: Annotated[str|None, Field(default="-",
                                                 description="Caractere especial utilizado para marcar colunas passadas sem correspondência na base de dados",
                                                 examples='"-"' )]

@router.post("/")
async def pesquisar(body: PesquisarRequest, excel: dp.Excel = Depends(dp.get_excel)):
    return excel.pesquisar(
        colunas=body.colunas,
        tabelas=body.tabelas,
        criterios=body.criterios,
        criterios_tabelas=body.criterios_tabelas,
        relacoes=body.relacoes,
        caractere_especial=body.caractere_especial
    )