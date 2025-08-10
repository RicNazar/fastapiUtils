from typing import Annotated,Any
from fastapi import APIRouter, Depends
from app.api.excel import dependencies as dp
from pydantic import BaseModel,Field

from app.api.excel.classes.excel import Excel

router = APIRouter()

@router.get("/")
async def carregar_exemplo():
    excel = Excel()
    excel.db.criar_tabelas()  # Cria as tabelas se não existirem
    
    # Exemplo de uso para atualizar (inclusão de registros em usuarios)
    usuarios = [
        ['id', 'name', 'email', 'idade', 'uf', 'observacao', 'salario', 'data_nascimento', 'eh_funcionario', 'interesses', 'MD'],
        [0, 'Ricardo', 'ricardo@example.com', 30, 'SP', 'Observação 1', 3000.0, '1990-01-01', True, ['interesse1', 'interesse2'], 'A'],
        [0, 'Maria', 'maria@example.com', 25, 'RJ', 'Observação 2', 2500.0, '1995-02-02', False, ['interesse2'], 'A'],
        [0, 'João', 'joao@example.com', 28, 'SP', 'Observação 3', 2800.0, '1992-03-03', True, ['interesse1'], 'A'],
    ]
    try:
        resultado = excel.atualizar('users', usuarios)
        return {"message": f"Exemplo de uso carregado com sucesso. Ids.:{resultado}"}
    except Exception as e:
        return {"error": str(e)}