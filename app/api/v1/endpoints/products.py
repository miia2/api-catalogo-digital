from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form, Query
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import database, security, services
from typing import Optional

router = APIRouter()

@router.get("/me", response_model=schemas.ProductPaginationOut)
def get_my_products(
    page: int = Query(1, ge=1, description="Número da página"),
    size: int = Query(20, ge=1, le=100, description="Itens por página"),
    search: Optional[str] = Query(None, description="Filtrar produtos por nome"),
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(security.get_current_user)
):
    query = db.query(models.Product).filter(models.Product.user_id == current_user.id)
    
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
        
    total_items = query.count()
    skip = (page - 1) * size
    produtos_paginados = query.offset(skip).limit(size).all()
    
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
    description: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: Optional[UploadFile] = File(None), # Imagem opcional para dar flexibilidade
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    url_da_imagem = None
    if image:
        try:
            url_da_imagem = services.upload_imagem_produto(image)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro no upload da imagem: {str(e)}")

    novo_produto = models.Product(
        name=name,
        price=price,
        description=description,
        is_available=is_available,
        image_url=url_da_imagem,
        user_id=current_user.id
    )
    
    db.add(novo_produto)
    db.commit()
    db.refresh(novo_produto)
    return novo_produto

# CORREÇÃO: PUT aceita FormData para alinhar com o envio do Dashboard.tsx
@router.put("/{product_id}", response_model=schemas.ProductOut)
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: Optional[str] = Form(None),
    is_available: bool = Form(True),
    image: Optional[UploadFile] = File(None), # Troca a imagem só se enviar uma nova
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(security.get_current_user)
):
    produto_banco = db.query(models.Product).filter(models.Product.id == product_id).first()
    if not produto_banco:
        raise HTTPException(status_code=404, detail="Produto não encontrado.")
    if produto_banco.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para editar este produto.")
    
    produto_banco.name = name
    produto_banco.price = price
    produto_banco.description = description
    produto_banco.is_available = is_available

    # Se enviou uma foto nova, atualiza no Cloudinary. Se não enviou, mantém a antiga!
    if image:
        try:
            produto_banco.image_url = services.upload_imagem_produto(image)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro no upload da nova imagem: {str(e)}")
        
    db.commit()
    db.refresh(produto_banco)
    return produto_banco

@router.delete("/{product_id}")
def delete_product(
    product_id: int, 
    db: Session = Depends(database.get_db), 
    current_user: models.User = Depends(security.get_current_user)
):
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
    user = db.query(models.User).filter(models.User.store_slug == slug).first()
    if not user:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
        
    query = db.query(models.Product).filter(models.Product.user_id == user.id)
    
    if search:
        query = query.filter(models.Product.name.ilike(f"%{search}%"))
        
    total_items = query.count()
    skip = (page - 1) * size
    produtos_paginados = query.offset(skip).limit(size).all()
    
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