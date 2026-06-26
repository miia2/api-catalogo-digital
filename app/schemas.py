import re
from pydantic import BaseModel, EmailStr, field_validator
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

    @field_validator('store_slug')
    @classmethod
    def validar_store_slug(cls, v: str) -> str:
        # 1. Converte automaticamente para minúsculas e remove espaços nas pontas
        slug_limpo = v.strip().lower()

        # 2. Expressão Regular (Regex):
        # ^[a-z0-7-]+$ significa: Começo ao fim da string só aceita letras minúsculas de a-z, números e hífen.
        if not re.match(r"^[a-z0-9-]+$", slug_limpo):
            raise ValueError(
                "O link da loja deve conter apenas letras minúsculas, números e hífens (ex: minha-loja-123). "
                "Espaços, acentos e caracteres especiais não são permitidos."
            )
        
        # 3. Evita que o usuário crie slugs vazios ou compostos apenas por hífens "---"
        if slug_limpo.replace("-", "") == "":
            raise ValueError("O link da loja não pode ser composto apenas por hífens.")

        return slug_limpo

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