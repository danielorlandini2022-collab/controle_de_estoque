from ..db import Base, engine
from .. import models  # registra mapeamentos

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    print('Tabelas criadas em estoque.db')
