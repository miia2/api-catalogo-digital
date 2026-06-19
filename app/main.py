from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
import os

app = FastAPI(title="SaaS Catálogo Digital Pro")

# 1. Definimos a lista de origens permitidas
# Adicione a URL que a Vercel gerar para o seu frontend assim que fizer o deploy dela lá
ORIGINS_PERMITIDAS = [
    "http://localhost:5173",     # URL padrão do Vite rodando localmente
    "http://127.0.0.1:5173",    # Alternativa local
    "https://seu-catalogo-frontend.vercel.app" # Substitua pela sua URL real da Vercel depois!
]

# 2. Injetamos a lista no middleware de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS_PERMITIDAS, # Trocado de ["*"] para a nossa lista restrita
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, PUT, DELETE apenas para as origens acima
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API do Catálogo Digital Online, Modular e Segura!"}