import os
import bcrypt 
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

# Limpamos o fallback para uma frase de aviso. O comprador deve gerar a dele no .env
SECRET_KEY = os.getenv("SECRET_KEY", "ALTERE_ESTA_CHAVE_SUPER_SECRETA_EM_PRODUCAO_POR_SEGURANCA")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

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
    expira = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    a_copiar.update({"exp": expira})
    return jwt.encode(a_copiar, SECRET_KEY, algorithm=ALGORITHM)