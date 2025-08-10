from datetime import datetime
import json
from typing import Annotated
import uuid
from fastapi import APIRouter, Depends
from app.api.excel import dependencies as dp

router = APIRouter()

def exemplo_para_tipo(tipo_str: str):
    # Remove parâmetros como "(50)" e normaliza para maiúsculo
    tipo = tipo_str.split("(")[0].strip().upper()

    if tipo in ("BIGINT", "INTEGER", "SMALLINT"):
        return 123456
    elif tipo in ("DECIMAL", "NUMERIC", "FLOAT", "DOUBLE", "REAL", "DOUBLE PRECISION"):
        return 1234.56
    elif tipo == "BOOLEAN":
        return True
    elif tipo in ("CHAR", "NCHAR", "VARCHAR", "NVARCHAR", "TEXT", "CLOB"):
        return "ExemploTexto"
    elif tipo == "DATE":
        return datetime.today().date()
    elif tipo in ("DATETIME", "TIMESTAMP"):
        return datetime.now().isoformat()
    elif tipo == "TIME":
        return datetime.today().time()
    elif tipo in ("BLOB", "BINARY", "VARBINARY", "_BINARY"):
        return b"\xDE\xAD\xBE\xEF"
    elif tipo == "UUID":
        return str(uuid.uuid4())
    elif tipo == "JSON":
        return json.dumps({"chave": "valor", "numero": 123})
    elif tipo == "NULL":
        return None
    elif tipo == "TUPLETYPE":
        return (1, "a", True)
    elif tipo == "USERDEFINEDTYPE":
        return "UserDefinedValue"
    else:
        # Valor genérico para tipos desconhecidos
        return f"-DESCONHECIDO-"
    
@router.get("/")
async def obter_estrutura(tabelas: Annotated[str,"Tabelas separadas por ;"]="", excel: dp.Excel = Depends(dp.get_excel)):
    tabelas_ok = [tabela.strip() for tabela in tabelas.split(";") if tabela.strip()]
    try:
        if len(tabelas_ok) == 0:
            result = excel.db.estrutura
        else:
            result =  excel.coletar_estrutura(tabelas_ok)
    except Exception as e:
        return {"error": str(e)}

    response = {}
    for tabela,dados in result.items():
        response[tabela] = {
            "colunas": [col for col, det in dados.items()] + ["MD"],
            "tipos_colunas": [det["tipo"] for col, det in dados.items()] + ["A ou D"],
            "colunas_exemplos": [exemplo_para_tipo(det["tipo"]) for col, det in dados.items()] + ["A ou D"],
            "colunas_obrigatorias": [col for col, det in dados.items() if not det.get("anulavel")] + ["MD"],
            "colunas_obrigatorias_exemplos": [exemplo_para_tipo(det["tipo"]) for col, det in dados.items() if not det.get("anulavel")] + ["A ou D"]
        }

    return response