from ..db import Base, engine, SessionLocal
from ..models import Usuario, TipoUsuario
from ..security import hash_password

if __name__ == '__main__':
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as db:
        exists = db.query(Usuario).filter(Usuario.email == 'admin@local').first()
        if exists:
            print(f'Admin já existe (id={exists.id})')
        else:
            u = Usuario(
                nome='Admin Global',
                email='admin@local',
                senha_hash=hash_password('admin123'),
                tipo=TipoUsuario.ADMIN,
                empresa_id=None
            )
            db.add(u)
            db.commit()
            print('Admin criado: admin@local / admin123 (altere depois)')
