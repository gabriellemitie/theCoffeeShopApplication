from sqlalchemy.orm import Session
from typing import Annotated

from database import SessionLocal
from fastapi import APIRouter, Depends
from models import Menu
from starlette import status

router = APIRouter(
    prefix='/menu',
    tags=['menu']
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

# cardapio da cafeteria
items = [
    Menu(item_name="Café expresso", price=5.0),
    Menu(item_name="Café coado", price=3.0),
    Menu(item_name="Cappuccino", price=7.0),
    Menu(item_name="Latte", price=6.5),
    Menu(item_name="Chá de hortelã", price=4.0),
    Menu(item_name="Suco de laranja", price=8.0),
    Menu(item_name="Croissant", price=4.5),
    Menu(item_name="Pão de queijo", price=2.5),
    Menu(item_name="Bolo de cenoura", price=6.0),
    Menu(item_name="Torrada com manteiga", price=3.5),
    Menu(item_name="Água s/ gás", price=3.0)
]

def inserir_itens(db: Session):
    for item in items:
        db.add(item)
    db.commit()

@router.get('/', status_code=status.HTTP_200_OK)
async def mostrar_cardapio(db: db_dependency):
    if db.query(Menu).count() == 0:
        inserir_itens(db)  # Insere os itens no banco, se necessário
    return db.query(Menu).all()