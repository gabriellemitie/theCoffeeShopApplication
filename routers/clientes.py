from typing import Annotated

from passlib.handlers.bcrypt import bcrypt
from pydantic import  Field
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from starlette.status import HTTP_200_OK

from database import SessionLocal
from models import Users
from passlib.context import CryptContext # criptografar e hash senhas
from .auth import get_current_user


# colocando a rota clientes
router = APIRouter(
    prefix='/clients',
    tags=['clients']
)

# conexao com o banco

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


# verificacao da senha antes de mudar
class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6) # field serve para 'formatar' o tipo do dado, no caso estamos especificando que a senha tem que ter no minimo 6 caracteres

# obtendo o cliente atual 
@router.get('/', status_code=status.HTTP_200_OK)
async def get_client (user: user_dependency, db: db_dependency):
    if user is None:
       raise HTTPException(status_code=401, detail='Autenticação falhou.')
    return db.query(Users).filter(Users.id == user.get('id')).first() # consulta no bd e retornando somente o primeiro resultado

# alterando a senha
@router.post('/password', status_code=status.HTTP_201_CREATED)
async def change_password(user: user_dependency, db: db_dependency, user_verification: UserVerification):
    if user is None:
        raise HTTPException(status_code=401, detail='Autenticação falhou.')
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()  # consulta no bd e retornando somente o primeiro resultado
    # se a senha nao bater
    if not bcrypt_context.verify(user_verification.password, user_model.hashed_password):
        raise HTTPException(status_code=401, detail='Erro na mudança de senha.')
    # se der certo, trocar senha
    # alterando a senha
    user_model.hashed_password = bcrypt_context.hash(user_verification.new_password)
    # colocando no banco de dados
    db.add(user_model)
    # fazendo o commit
    db.commit()

    return {"Senha alterada com sucesso!"}
