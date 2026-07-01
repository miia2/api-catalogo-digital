from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings
import os

app = FastAPI(title="SaaS Catálogo Digital Pro")

# 1. Definimos APENAS os endereços do FRONTEND aqui
ORIGINS_PERMITIDAS = [
    "http://localhost:5173",                     # Frontend rodando no seu computador
    "http://127.0.0.1:5173",                    # Alternativa de IP local do Frontend
    "https://portfolio-v2-phi-ebon.vercel.app"   # Frontend oficial publicado na Vercel
]

# 2. Injetamos a lista no middleware de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=ORIGINS_PERMITIDAS, 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API do Catálogo Digital Online, Modular e Segura!"}