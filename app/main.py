from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
import app.core.models as models, app.schemas as schemas, app.core.database as database, security

app = FastAPI(title="SaaS Catálogo Digital")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# No main.py, logo após o app.add_middleware(...)
@app.get("/")
def read_root():
    return {"status": "API do Catálogo Digital Online e Pronta!"}

models.Base.metadata.create_all(bind=database.engine)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_current_user(db: Session = Depends(database.get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=401, detail="Não autorizado")
    try:
        payload = security.jwt.decode(token, security.SECRET_KEY, algorithms=[security.ALGORITHM])
        email: str = payload.get("sub")
        if email is None: raise credentials_exception
    except security.jwt.JWTError:
        raise credentials_exception
    user = db.query(models.User).filter(models.User.email == email).first()
    if user is None: raise credentials_exception
    return user

@app.post("/register", response_model=schemas.UserOut)
def register_user(user: schemas.UserCreate, db: Session = Depends(database.get_db)):
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(status_code=400, detail="E-mail já existe")
    if db.query(models.User).filter(models.User.store_slug == user.store_slug).first():
        raise HTTPException(status_code=400, detail="Este link de loja já está em uso")
    
    hashed_pwd = security.gerar_hash_senha(user.password)
    new_user = models.User(
        full_name=user.full_name, email=user.email, hashed_password=hashed_pwd,
        whatsapp_number=user.whatsapp_number, store_slug=user.store_slug
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verificar_senha(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    token_real = security.criar_token_acesso(data={"sub": user.email})
    return {"access_token": token_real, "token_type": "bearer", "store_slug": user.store_slug}

@app.post("/products", response_model=schemas.ProductOut)
def criar_produto(product: schemas.ProductCreate, db: Session = Depends(database.get_db), current_user: models.User = Depends(get_current_user)):
    novo_produto = models.Product(**product.model_dump(), user_id=current_user.id)
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

# ROTA DE ATUALIZAR (EDITAR PRODUTO)
@app.put("/products/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int, 
    product_update: schemas.ProductUpdate, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user) # Exige estar logado!
):
    # 1. Busca o produto no banco de dados
    produto_banco = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    # 2. Verifica se o produto existe
    if not produto_banco:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
        
    # 3. SUPER IMPORTANTE: Verifica se o produto pertence ao usuário logado
    if produto_banco.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este produto.")
    
    # 4. Atualiza apenas os campos que o usuário enviou
    # O exclude_unset=True garante que ele não apague dados se o usuário mandar só o preço novo
    update_data = product_update.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(produto_banco, key, value) # Muda o valor no objeto
        
    db.commit() # Salva no banco
    db.refresh(produto_banco) # Atualiza a variável com os dados novos
    
    return produto_banco


# ROTA DE EXCLUIR PRODUTO
@app.delete("/products/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user) # Exige estar logado!
):
    # 1. Busca o produto
    produto_banco = db.query(models.Product).filter(models.Product.id == product_id).first()
    
    # 2. Verifica se existe
    if not produto_banco:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
        
    # 3. Verifica se o usuário é o dono real do produto
    if produto_banco.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir este produto.")
        
    # 4. Exclui o produto
    db.delete(produto_banco)
    db.commit()
    
    return {"message": "Produto excluído com sucesso!"}

# Adicione esta rota no seu main.py
@app.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(get_current_user)):
    """Retorna os dados do lojista que está logado atualmente"""
    return current_user

# ROTA PARA O PAINEL DO LOJISTA VER SEUS PRÓPRIOS PRODUTOS
@app.get("/products/me", response_model=list[schemas.ProductOut])
def get_my_products(
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(get_current_user)
):
    # Retorna APENAS os produtos do usuário logado
    produtos = db.query(models.Product).filter(models.Product.user_id == current_user.id).all()
    return produtos

# ROTA PÚBLICA (Sem verificação de token!)
@app.get("/store/{slug}", response_model=schemas.StoreProfile)
def get_store_catalog(slug: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.store_slug == slug).first()
    if not user:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return user