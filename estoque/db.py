from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from .config import DATABASE_URL

# Recomendações para conexões estáveis com MariaDB/MySQL
# - pool_pre_ping=True para drenar conexões “mortas”
# - pool_recycle=3600 para reciclar conexões antes do timeout do servidor
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # testa a conexão antes de usar
    pool_recycle=3600,   # recicla conexões a cada 1h (ajuste conforme seu wait_timeout)
)

@event.listens_for(engine, 'connect')
def set_sqlite_pragma(dbapi_connection, connection_record):
    # Mantido por compatibilidade; sem efeito para MariaDB.
    pass
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,  # evita DetachedInstanceError na UI
    future=True
)

class Base(DeclarativeBase):
    pass