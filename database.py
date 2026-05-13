import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base # <-- Adicionado aqui
from dotenv import load_dotenv

load_dotenv()

# Pega o link do banco do .env. Se não achar, usa o SQLite de backup para testes
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./catalogo.db")

# O SQLite precisa de "check_same_thread", o Postgres não pode ter isso.
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
else:
    engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# A BASE QUE ESTAVA FALTANDO!
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()