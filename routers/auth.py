from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
from database import SessionLocal


router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

# gerando uma secret key
SECRET_KEY = 'da37459bca62dc6f43b0119cf004fcc11a4c89a818fd8f5c933748bb17ac77e5'
ALGORITHM = 'HS256'

# tratamento de segurança das senhas
# hasheando a senha e depois comparando
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto') # tipo bcrypt e deprecated para atualizar o tipo de hash se o passlib tornar algo obselto
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # autenticacao de senha e usuario

class CreateUserRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str


class Token(BaseModel):
    access_token: str
    token_type: str

def get_db():
    db = SessionLocal()
    try:
        yield db # yield = so vai executar o que tiver antes
    finally: # executa dps do primeiro der certo
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

# token que vai retornar as infos do cliente dps
def create_access_token(username: str, user_id: int, role: str, expires_delta:timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm= ALGORITHM)

# func para obter o cliente atual
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: str = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Não foi possível validar o usuário.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Não foi possível validar o usuário.')

# criandeo usuario
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    create_user_model = Users(
        email = create_user_request.email,
        username = create_user_request.username,
        role = create_user_request.role,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        is_active = True
    )
    db.add(create_user_model)
    db.commit()
    return {"Usuário criado com sucesso!"}

# token de acesso
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db:db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Não foi possível validar o usuário.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))
    return {'access_token': token, 'token_type': 'bearer'}
