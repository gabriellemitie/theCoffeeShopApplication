from typing import Annotated
from fastapi import APIRouter
from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from starlette import status

from models import Orders, Menu
from database import SessionLocal

from .auth import get_current_user


router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

def get_db():
    db = SessionLocal()
    try:
        yield db # yield = so vai executar o que tiver antes
    finally: # executa dps do primeiro der certo
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

# modelo item novo
class CreateItemRequest(BaseModel):
    item_name: str
    price: float




# criando get para poder ler todos os pedidos
@router.get('/orders', status_code=status.HTTP_200_OK)
async def read_all_orders(user: user_dependency, db: db_dependency):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Autenticação falhou.')
    # fazendo a consulta dos pedidos
    orders = db.query(Orders).all()
    # pegando infos e montando o template dos pedidos
    response = []
    for order in orders:
        order_data = {
            'order_id': order.order_id,
            'username': order.username,
            'complete': order.complete,
            'items': []
        }
        # adicionando os items do pedido
        for item in order.items:
            item_data = {
                'item_name': item.item_name,
                'quantity': item.quantity,
                'observations': item.observations
            }
            order_data['items'].append(item_data)

        response.append(order_data)

    return response



# concluir pedido
@router.put("/finish-orders/{order_id}", status_code=status.HTTP_200_OK)
async def finish_order(user: user_dependency, db: db_dependency, order_id: int):
     if user is None or user.get('user_role') != 'admin':
         raise HTTPException(status_code=401, detail='Autenticação falhou.')
         # verificando se o id solicitado bate com o id do pedido feito
     order_model = db.query(Orders).filter(Orders.order_id == order_id).first()
     # se for pedido vazio
     if order_model is None:
         raise HTTPException(status_code=404, detail='Pedido não encontrado.')
     order_model.complete = True
     db.commit()
     db.refresh(order_model)

     return {f"Pedido número {order_id} finalizado!"}



# adicionar mais itens no cardapio
@router.post("/new_items", status_code=status.HTTP_201_CREATED)
async def add_new_items(user: user_dependency, db: db_dependency, create_item_request: CreateItemRequest):
    # verificando se é admin
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Autenticação falhou.')
    # criando novo item
    create_item_model = Menu(
        item_name = create_item_request.item_name,
        price = create_item_request.price
    )

    db.add(create_item_model)
    db.commit()
    db.refresh(create_item_model)

    # retorna o nome do item e o ID que foi gerado
    return {
        "message": f"Item '{create_item_model.item_name}' foi adicionado ao cardápio!",
        "item_id": create_item_model.item_id,
        "preço": create_item_model.price
    }

# deletando pedidos pos conclusao = limpeza dos pedidos
@router.delete("/clean-orders/{complete}")
async def clean_orders(db: db_dependency, user: user_dependency, complete: bool):
    if user is None or user.get('user_role') != 'admin':
        raise HTTPException(status_code=401, detail='Autenticação falhou.')
    order_cl = db.query(Orders).filter(Orders.complete == complete).all() # apaga todos que forem True
    for order_complete in order_cl:
        db.delete(order_complete)
    db.commit()
    return {"message": "Pedidos concluídos deletados com sucesso!", "deleted_orders_count": len(order_cl)}



