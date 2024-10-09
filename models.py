# modelos que serao inseridos no bd depoi
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float

# criando uma nova classe
class Users(Base):
    #nome da nova tabela
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(16), unique=True)
    email = Column(String(20), unique=True)
    # refaz o hash e compara com o que foi recebido
    hashed_password = Column(String(1000))
    is_active = Column(Boolean, default=True)
    role = Column(String(10))

# cardapio
class Menu(Base):
    __tablename__ = 'menu'
    item_id = Column(Integer, primary_key=True, index=True)
    item_name = Column(String(50), unique=True)
    price = Column(Float, nullable=False)


# pedidos cliente
class Orders(Base):
    __tablename__ = 'orders'
    # colunas da tabela
    order_id = Column(Integer, primary_key=True, index=True) # nova coluna e vai ser do tipo int
    username = Column(String(16), ForeignKey('users.username'))
    complete = Column(Boolean, default=False) #0 = false, 1 = true in database
    # fk
    user_id = Column(Integer, ForeignKey('users.id'))
    items = relationship("OrderItems", back_populates="order")

# criando nova tabela de items do pedido, melhor pratica inves de usar o array
class OrderItems(Base):
    __tablename__ = 'order_items'
    items_id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey('orders.order_id'))
    item_name = Column(String(20), ForeignKey('menu.item_name'))  # nome do item
    observations = Column(String(500))
    quantity = Column(Integer)  # quantidade do item
    order = relationship("Orders", back_populates="items")