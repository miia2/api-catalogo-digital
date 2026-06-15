import bcrypt 
from datetime import datetime, timedelta
from jose import jwt, JWTError               # Alterado para 'jose' que você já usa
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core import database
from app import models
from app.core.config import settings


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Configura de onde o FastAPI vai extrair o token (da rota de login)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- Funções de Criptografia e Token ---

def gerar_hash_senha(senha: str):
    """Transforma a senha em um hash seguro usando bcrypt direto"""
    pwd_bytes = senha.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hash_bytes.decode('utf-8') 

def verificar_senha(senha_pura: str, senha_hash: str):
    """Confere se a senha pura bate com o hash salvo"""
    try:
        pwd_bytes = senha_pura.encode('utf-8')
        hash_bytes = senha_hash.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except Exception:
        return False

def criar_token_acesso(data: dict):
    a_copiar = data.copy()
    # datetime.utcnow() foi descontinuado em versões novas do Python, usamos zone-aware ou utcnow padrão do jose
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    a_copiar.update({"exp": expira})
    return jwt.encode(a_copiar, SECRET_KEY, algorithm=ALGORITHM)

# --- Dependência de Autenticação ---

def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    """Injeta o usuário logado nas rotas protegidas decodificando o JWT"""
    credentials_exception = HTTPException(status_code=401, detail="Não autorizado")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None: 
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: 
        raise credentials_exception
    return user