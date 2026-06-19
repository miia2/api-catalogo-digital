import cloudinary
import cloudinary.uploader
from fastapi import UploadFile
from app.core.config import settings

# Inicializa a configuração do Cloudinary com as chaves do seu .env
cloudinary.config(
    cloud_name=settings.CLOUDINARY_CLOUD_NAME,
    api_key=settings.CLOUDINARY_API_KEY,
    api_secret=settings.CLOUDINARY_API_SECRET,
    secure=True
)

def upload_imagem_produto(file: UploadFile) -> str:
    """Envia a imagem para o Cloudinary e retorna a URL segura"""
    try:
        # Envia o arquivo diretamente da memória para a nuvem
        resultado = cloudinary.uploader.upload(
            file.file,
            folder="catalogo_produtos", # Cria uma pasta organizada no Cloudinary
            transformation=[
                {"width": 800, "height": 800, "crop": "limit"}, # Redimensiona se for gigante
                {"quality": "auto"}, # Otimiza o peso automaticamente
                {"fetch_format": "auto"} # Converte para formatos modernos como WebP
            ]
        )
        # Retorna apenas a URL gerada pela nuvem
        return resultado.get("secure_url")
    except Exception as e:
        raise Exception(f"Erro ao fazer upload da imagem: {str(e)}")