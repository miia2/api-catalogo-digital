from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.orm import Session
from app import models, schemas
from app.core import database, security, services

router = APIRouter()

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

@router.get("/me", response_model=list[schemas.ProductOut])
def get_my_products(db: Session = Depends(database.get_db), current_user: models.User = Depends(security.get_current_user)):
    return db.query(models.Product).filter(models.Product.user_id == current_user.id).all()

@router.get("/store/{slug}", response_model=schemas.StoreProfile)
def get_store_catalog(slug: str, db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.store_slug == slug).first()
    if not user:
        raise HTTPException(status_code=404, detail="Loja não encontrada")
    return user