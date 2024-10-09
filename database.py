from sqlalchemy import create_engine

from sqlalchemy.orm import sessionmaker ,declarative_base




# criando o local do nosso db, estara nesse diretorio
SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:senha123@127.0.0.1:3306/coffeeShop' # fazendo a conexao com o nosso bd

# criando mecanismo para o app -> abrir conexao com o db
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# instancia do local de db
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine) # impede que as transacoes facam algo automaticamente

#depois de criar poderemos chamar o objeto base para controlar o bd
Base = declarative_base()



