"""
Script opcional para copiar dados de um SQLite legado (sistema.db). Adapte conforme seu schema antigo.
"""

    import os, sqlite3
    from ..db import Base, engine, SessionLocal
    from ..models import Empresa, Usuario, Produto, TipoUsuario

    if __name__ == '__main__':
        Base.metadata.create_all(bind=engine)
        src_path = 'sistema.db'
        if not os.path.exists(src_path):
            print('Base antiga sistema.db não encontrada, nada a migrar.')
            raise SystemExit(0)
        con = sqlite3.connect(src_path)
        cur = con.cursor()

        # Empresas
        try:
            for row in cur.execute('SELECT id, nome, cnpj, telefone FROM empresa'):
                with SessionLocal() as db:
                    db.merge(Empresa(id=row[0], nome=row[1], cnpj=str(row[2]), telefone=row[3] if len(row)>3 else None))
                    db.commit()
        except Exception as e:
            print('[Aviso] Não foi possível migrar empresas:', e)

        # Usuários
        try:
            for row in cur.execute('SELECT id, nome, email, senha FROM usuarios'):
                with SessionLocal() as db:
                    db.merge(Usuario(id=row[0], nome=row[1], email=row[2], senha_hash=row[3], tipo=TipoUsuario.PADRAO, empresa_id=None))
                    db.commit()
        except Exception as e:
            print('[Aviso] Não foi possível migrar usuários:', e)

        # Produtos
        try:
            for row in cur.execute('SELECT id, nome, preco, quantidade FROM produtos'):
                with SessionLocal() as db:
                    db.merge(Produto(id=row[0], empresa_id=1, codigo=f"LEG-{row[0]}", descricao=row[1], estoque=int(row[3] or 0)))
                    db.commit()
        except Exception as e:
            print('[Aviso] Não foi possível migrar produtos:', e)

        con.close()
        print('Migração básica concluída.')
