import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.api import api_router
from app.core.config import settings

# --- RODAR AS MIGRAÇÕES AUTOMATICAMENTE APENAS EM PRODUÇÃO ---
# Isso evita conflitos quando você estiver testando localmente no seu computador
# if os.getenv("RENDER") or os.getenv("DATABASE_URL"):
    # try:
       # print("Iniciando migrações automáticas do Alembic na nuvem...")
       # import alembic.config
       # alembic.config.main(argv=["upgrade", "head"])
       # print("Migrações concluídas com sucesso!")
   # except Exception as e:
      #  print(f"Aviso: Não foi possível rodar o Alembic automaticamente ({e}).")
# -------------------------------------------------------------

app = FastAPI(title="SaaS Catálogo Digital Pro")

# 1. Definimos APENAS os endereços do FRONTEND aqui
ORIGINS_PERMITIDAS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",                    # Alternativa de IP local do Frontend
    "https://portfolio-v2-6p1w2zjfh-miia2s-projects.vercel.app",   # Frontend oficial publicado na Vercel
]

# 2. Injetamos a lista no middleware de segurança
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"status": "API do Catálogo Digital Online, Modular e Segura!"}