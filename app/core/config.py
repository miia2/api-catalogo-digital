import os
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # 1. Configurações Globais da API
    PROJECT_NAME: str = "SaaS Catálogo Digital"
    API_V1_STR: str = "/api/v1"
    
    # 2. Segurança e JWT (Serão lidos do seu arquivo .env automaticamente)
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # 3. Banco de Dados (Configuração padrão para SQLite local)
    # Se você for usar PostgreSQL em produção, basta alterar no .env
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Configuração para o Pydantic buscar o arquivo .env correto na raiz do projeto
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_ignore_empty=True,
        extra="ignore"
    )

# Instanciamos a classe para importar direto nos outros arquivos
settings = Settings()