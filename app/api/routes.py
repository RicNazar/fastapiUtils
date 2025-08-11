import os
from fastapi import APIRouter, Depends, HTTPException, status
from app.api.excel.routes import router as excel_router
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

# 1 — Configurar esquema de segurança (Bearer)
bearer_scheme = HTTPBearer(auto_error=True)

# 2 — Função para validar token
def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    load_dotenv()
    if token != os.getenv("EXCEL_TOKEN"):  # aqui você aplica a lógica real de validação
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido 'excel-token' ou ausente",
            headers={"excel-token": "Bearer"},
        )
    return token  # opcional: pode retornar payload decodificado do JWT

# 3 — Criar o router com autenticação obrigatória
router = APIRouter()

router.include_router(excel_router, prefix="/excel", tags=["excel"],dependencies=[Depends(verify_token)])  # aplica para todas as rotas desse router

@router.get("/",include_in_schema=False)
async def apis():
    return {"status": "Ok"}

'''
{
  "tabela": "users",
  "matriz": 
[
      [
      "id",
      "name",
      "email",
      "idade",
      "uf",
      "observacao",
      "salario",
      "data_nascimento",
      "eh_funcionario",
      "interesses",
      "MD"
    ],[
      0,
      "ExemploTexto",
      "ExemploTextoEmail",
      123456,
      "PR",
      "ExemploTexto",
      1234.56,
      "2025-08-10",
      true,
      ["a","b","c"],
      "A"
    ]]
}
'''