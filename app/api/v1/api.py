from fastapi import APIRouter
from app.api.v1.endpoints import auth, products

api_router = APIRouter()

# 1. Rotas de Autenticação (/api/v1/auth/...)
api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(auth.router, tags=["Legado Auth"])

# 2. Rotas de Produtos (/api/v1/products/...)
api_router.include_router(products.router, prefix="/products", tags=["Produtos & Lojas"])

# 🌟 3. ATALHO DA VITRINE: Permite chamar /api/v1/store/{slug} sem precisar do /products na frente!
api_router.include_router(products.router, tags=["Vitrine Pública"])