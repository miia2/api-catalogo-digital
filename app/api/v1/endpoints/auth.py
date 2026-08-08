from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app import schemas, models
from app.core import database, security

router = APIRouter()

@router.post("/register", response_model=schemas.UserOut)
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

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(database.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not security.verificar_senha(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="E-mail ou senha incorretos")
    
    token_real = security.criar_token_acesso(data={"sub": user.email})
    return {"access_token": token_real, "token_type": "bearer", "store_slug": user.store_slug}

# Esta linha única agora atende tanto /auth/me quanto /users/me de forma limpa
@router.get("/me", response_model=schemas.UserOut)
@router.get("/users/me", response_model=schemas.UserOut)
def read_users_me(current_user: models.User = Depends(security.get_current_user)):
    return current_user

@router.post("/forgot-password")
def forgot_password(
    body: schemas.ForgotPasswordRequest, 
    db: Session = Depends(database.get_db)
):
    user = db.query(models.User).filter(models.User.email == body.email).first()
    
    # ⚠️ Segurança: Por boas práticas, mesmo se o e-mail não existir, 
    # retornamos 200 OK para evitar que hackers descubram e-mails cadastrados.
    if user:
        token = security.criar_token_recuperacao(user.email)
        
        # Link que o usuário vai clicar no e-mail (ajuste a URL para o domínio do seu frontend na Vercel)
        link_reset = f"https://seu-frontend.vercel.app/reset-password?token={token}"
        
        # TODO: Enviar o e-mail real aqui (imprimindo no console da Render por enquanto)
        print(f"📧 [RECUPERAÇÃO DE SENHA] Enviar para {user.email}: {link_reset}")
        
    return {"message": "Se o e-mail estiver cadastrado, você receberá o link para redefinir sua senha."}


@router.post("/reset-password")
def reset_password(
    body: schemas.ResetPasswordRequest, 
    db: Session = Depends(database.get_db)
):
    email = security.verificar_token_recuperacao(body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Token inválido ou expirado.")
        
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
        
    # Atualiza a senha do usuário com o novo Hash
    user.hashed_password = security.gerar_hash_senha(body.new_password)
    db.commit()
    
    return {"message": "Senha redefinida com sucesso! Você já pode fazer login."}