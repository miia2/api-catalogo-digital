from pydantic import BaseModel, EmailStr
from typing import List, Optional

# --- Produtos ---
class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    is_available: bool = True

class ProductCreate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# --- Usuários / Loja ---
class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    whatsapp_number: str
    store_slug: str

class UserOut(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    whatsapp_number: str
    store_slug: str

    class Config:
        from_attributes = True

# Perfil da Loja Pública com a lista de produtos
class StoreProfile(UserOut):
    products: List[ProductOut] = []

# No final do seu schemas.py:

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: Optional[bool] = None    

class ProductPaginationOut(BaseModel):
    items: List[ProductOut]  # A lista com os 20 produtos da página atual
    total: int               # O total de produtos que o lojista tem no banco (ex: 150)
    page: int                # O número da página atual
    size: int                # A quantidade de itens por página

    class Config:
        from_attributes = True    