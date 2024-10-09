
from database import engine
from fastapi import FastAPI
from routers import auth, admin, clientes, pedidos, menu
from models import Base
# criando a api
app = FastAPI()

Base.metadata.create_all(bind=engine)

# criando rotas -> o que acontece quando o user entra em x lugar



app.include_router(menu.router)
app.include_router(auth.router)
app.include_router(clientes.router)
app.include_router(pedidos.router)
app.include_router(admin.router)


