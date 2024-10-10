from typing import Annotated, List
from fastapi import APIRouter, Request
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import SessionLocal
from models import OrderItems, Orders, Menu
from routers.admin import db_dependency
from routers.auth import get_current_user
from routers.clientes import user_dependency
from pydantic import BaseModel, Field

# criando rota
router = APIRouter(
    prefix='/orders',
    tags=['orders']
)

# conexao com banco
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency= Annotated[dict, Depends(get_current_user)]


# formato dos itens do pedido
class OrderItemRequest(BaseModel):
    item_name: str
    quantity: int
    observations: str = Field(max_length=400)

# formato do pedido
class OrderRequest(BaseModel):
    items: List[OrderItemRequest] # lista com itens do pedido

# criando um novo pedido
@router.post("/new-order/", status_code=status.HTTP_201_CREATED)
async def create_order(user: user_dependency, db: db_dependency, order_request: OrderRequest):
    # validando o usuário
    if user is None:
        raise HTTPException(status_code=401, detail='Authentication failed')

    total = 0  # valor total do pedido
    valid_items = []  # lista para armazenar os itens válidos do pedido

    # validando se todos os itens estão no cardápio
    for item in order_request.items:
        menu_item = db.query(Menu).filter(Menu.item_name.ilike(f"%{item.item_name}%")).first()
        if menu_item is None:
            raise HTTPException(status_code=404, detail=f'Ainda não temos {item.item_name} no cardápio :(')

        # se o item está no cardápio, calculamos o total do pedido
        item_price = menu_item.price
        item_total = item_price * item.quantity
        total += item_total

        # adiciona o item na lista
        valid_items.append({
            'item_name': item.item_name,
            'quantity': item.quantity,
            'observations': item.observations,
            'price': item_price
        })

   # criando somente depois de validar tudo
    order_model = Orders(
        complete=False,
        user_id=user.get('id'),
        username=user.get('username')
    )

    db.add(order_model)
    db.commit()
    db.refresh(order_model)

    # inserindo os itens que existem mesmo no cardapio no banco
    # isso garante que nao se criem pedidos vazios poluindo o banco
    for valid_item in valid_items:
        item_order_model = OrderItems(
            order_id=order_model.order_id,
            item_name=valid_item['item_name'],
            quantity=valid_item['quantity'],
            observations=valid_item['observations']
        )
        db.add(item_order_model)

    db.commit()

    return {'total do seu pedido R$': total, 'message': 'Pedido criado com sucesso!'}


# retornando 'meus pedidos'
@router.get("/my_orders/{username}", status_code=status.HTTP_200_OK)
async def meus_pedidos(user: user_dependency, db: db_dependency, user_name: str):
    if user is None:
        raise HTTPException(status_code=401, detail='Autenticação falhou')
    my_orders = db.query(Orders).filter(Orders.username == user_name).all()
    return my_orders








