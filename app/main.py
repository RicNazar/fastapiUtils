#Core
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

#imports
from app.api.routes import router as api_router

#Criação da instância do FastAPI
app = FastAPI()
templates = Jinja2Templates(directory="app/htmlTemplates")

# Para servir arquivos estáticos (CSS, JS, imagens) da pasta "static"
app.mount("/static", StaticFiles(directory="app/static"), name="static")

#páginas estáticas
routes = [
    {"name": "Home", "path": "/"},
    {"name": "API Docs", "path": "/docs"},
    {"name": "ReDoc", "path": "/redoc"},
]
context = {"title": "FastApi Utils","content": "Utilitários para o FastApi","routes": routes}
paginaInicial = templates.get_template("home.html").render(context)

#adição do roteador de API
app.include_router(api_router, prefix="/api")

@app.get("/", response_class=HTMLResponse,include_in_schema=False)
async def home():
    return paginaInicial

