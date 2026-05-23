Crie um arquivo .env na raiz da pasta backend baseando-se no arquivo .env.example:

DATABASE_URL=postgresql://seu_usuario:sua_senha@seu_host/seu_banco?sslmode=require
SECRET_KEY=sua_chave_secreta_jwt_aqui
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

Nota: Se DATABASE_URL não for preenchida, o sistema utilizará o SQLite (catalogo.db) automaticamente para testes locais de desenvolvimento.

Para rodar o servidor backend localmente:

uvicorn main:app --reload

Acesse a documentação interativa (Swagger) em: http://127.0.0.1:8000/docs