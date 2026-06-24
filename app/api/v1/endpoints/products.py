from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import database, security, services
from typing import Optional

router = APIRouter()

@router.get("/me", response_model=schemas.ProductPaginationOut) # Alterado o response_model
def get_my_products(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Filtrar produtos por nome"),
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(security.get_current_user)
):
    # 1. Criamos a query base filtrando pelo usuário logado
    query = db.query(models.Product).filter(models.Product.user_id == current_user.id)
    
    # 2. Se o usuário enviou um termo de busca, aplicamos o filtro (IgnoreCase / ILIKE)
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
        
    # 3. Contamos o total de itens que batem com os filtros (antes de paginar)
    total_items = query.count()
    
    # 4. Calculamos o pulo (offset) e aplicamos a paginação
    # Ex: Página 1: (1-1)*20 = offset 0. Página 2: (2-1)*20 = offset 20.
    skip = (page - 1) * size
    produtos_paginados = query.offset(skip).limit(size).all()
    
    # 5. Retornamos o objeto estruturado com os metadados
    return {
        "items": produtos_paginados,
        "total": total_items,
        "page": page,
        "size": size
    }

@router.post("/", response_model=schemas.ProductOut)
def criar_produto(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    is_available: bool = Form(True),
    image: UploadFile = File(...), # Exige o envio do arquivo de imagem
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    # 1. Envia a imagem recebida para o Cloudinary e pega a URL
    try:
        url_da_imagem = services.upload_imagem_produto(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # 2. Salva o produto no banco de dados com a URL da nuvem
    novo_produto = models.Product(
        name=name,
        price=price,
        description=description,
        is_available=is_available,
        image_url=url_da_imagem, # Grava a URL estável do Cloudinary
        user_id=current_user.id
    )
    
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(product_id: int, product_update: schemas.ProductUpdate, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    produto_banco = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not produto_banco:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    if produto_banco.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este produto.")
    
    update_data = product_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(produto_banco, key, value)
        
    db.commit()
    db.refresh(produto_banco)
    return produto_banco

@router.delete("/{product_id}")
def delete_product(product_id: int, db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    produto_banco = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not produto_banco:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    if produto_banco.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para excluir este produto.")
        
    db.delete(produto_banco)
    db.commit()
    return {"message": "Produto excluído com sucesso!"}

@router.get("/store/{slug}")
def get_store_catalog(
    slug: str,
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: Session = Depends(database.get_db)
):
    # 1. Busca o lojista pelo slug
    user = db.query(models.User).filter(models.User.store_slug == slug).first()
    if not user:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
        
    # 2. Monta a query de produtos dessa loja específica
    query = db.query(models.Product).filter(models.Product.user_id == user.id)
    
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
        
    total_items = query.count()
    skip = (page - 1) * size
    produtos_paginados = query.offset(skip).limit(size).all()
    
    # Retornamos os dados do perfil da loja e os produtos paginados separadamente
    return {
        "store_info": {
            "id": user.id,
            "full_name": user.full_name,
            "store_slug": user.store_slug,
            "whatsapp_number": user.whatsapp_number
        },
        "products_pagination": {
            "items": [schemas.ProductOut.model_validate(p) for p in produtos_paginados],
            "total": total_items,
            "page": page,
            "size": size
        }
    }