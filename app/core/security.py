from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.core import database
from app import models
from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Inicializa o construtor de senhas leve e otimizado para nuvem
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configura de onde o FastAPI vai extrair o token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# --- Funções de Criptografia e Token Otimizadas ---

def gerar_hash_senha(senha: str):
    """Transforma a senha em um hash usando o motor otimizado da passlib"""
    return pwd_context.hash(senha)

def verificar_senha(senha_pura: str, senha_hash: str):
    """Confere a senha com consumo de CPU reduzido, ideal para instâncias gratuitas"""
    try:
        return pwd_context.verify(senha_pura, senha_hash)
    except Exception as e:
        print(f"Erro na verificação de senha: {e}")
        return False

def criar_token_acesso(data: dict):
    a_copiar = data.copy()
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    a_copiar.update({"exp": expira})
    return jwt.encode(a_copiar, SECRET_KEY, algorithm=ALGORITHM)

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