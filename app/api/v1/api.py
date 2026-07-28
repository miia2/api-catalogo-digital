from fastapi import APIRouter
from app.api.v1.endpoints import auth, products

api_router = APIRouter()

# 1. Rotas oficiais (/api/v1/auth/login, /api/v1/auth/register, /api/v1/auth/me)
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])

# 2. REDE DE SEGURANÇA: Permite que chamadas sem o /auth (ex: /api/v1/users/me) também funcionem!
api_router.include_router(auth.router, tags=["Legado"])

# 3. Rotas de produtos (/api/v1/products/...)
api_router.include_router(products.router, prefix="/products", tags=["Produtos & Lojas"])