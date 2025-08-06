@echo off
REM Desativa a exibição dos comandos no terminal (visual mais limpo)

REM Ativa o ambiente virtual Python (assumindo que ele está em .venv\)
call .venv\Scripts\activate.bat

REM Mostra uma mensagem de status
echo Ambiente virtual ativado.

REM Instala as dependências do projeto (caso necessário)
pip install -r requirements.txt

REM Inicia o servidor FastAPI em modo desenvolvimento (hot reload ativado)
uvicorn app.main:app --reload

REM Mantém a janela aberta após o término
pause