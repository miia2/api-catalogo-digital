import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # Adicionamos o declarative_base aqui
from dotenv import load_dotenv

load_dotenv()

# No seu database.py, logo após o load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

# ADICIONE ESTAS LINHAS AQUI:
if SQLALCHEMY_DATABASE_URL and SQLALCHEMY_DATABASE_URL.startswith("postgres://"):
    SQLALCHEMY_DATABASE_URL = SQLALCHEMY_DATABASE_URL.replace("postgres://", "postgresql://", 1)

# Se não houver URL (testes locais), usa o SQLite
if not SQLALCHEMY_DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./catalogo.db"

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./catalogo.db")

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# ESSA LINHA ABAIXO É A QUE ESTÁ FALTANDO:
Base = declarative_base() 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()