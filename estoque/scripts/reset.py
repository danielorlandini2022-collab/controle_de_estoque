# estoque/scripts/reset_schema_safe.py
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.exc import SQLAlchemyError
from ..config import DATABASE_URL
from ..db import Base
from .. import models  # registra os mapeamentos

DB_NAME = "controle_estoque"

def _url_without_db(url_str: str) -> str:
    # remove o /database da URL para permitir CREATE DATABASE IF NOT EXISTS
    if "://" not in url_str:
        return url_str
    if "?" in url_str:
        main, q = url_str.split("?", 1)
        q = "?" + q
    else:
        main, q = url_str, ""
    if "/" in main.rsplit("@", 1)[-1]:
        head = main.rsplit("/", 1)[0]
        return head + q
    return url_str

def ensure_database():
    root_url = _url_without_db(DATABASE_URL)
    eng = create_engine(root_url, future=True, pool_pre_ping=True)
    with eng.begin() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;"))
    eng.dispose()

def create_missing_tables():
    eng = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
    try:
        # cria tabelas faltantes conforme o modelo ATUAL (TIMESTAMP, email=191, etc.)
        Base.metadata.create_all(bind=eng)
        print("Tabelas criadas/verificadas com sucesso.")
    finally:
        eng.dispose()

def apply_alters_if_needed():
    eng = create_engine(DATABASE_URL, future=True, pool_pre_ping=True)
    insp = inspect(eng)
    try:
        with eng.begin() as conn:
            # Ajusta defaults só se as tabelas existirem (para bases antigas)
            if insp.has_table("empresa"):
                try:
                    conn.execute(text(
                        "ALTER TABLE `empresa` "
                        "MODIFY `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;"
                    ))
                    print("ALTER empresa.created_at aplicado (ou já estava correto).")
                except SQLAlchemyError:
                    pass
            if insp.has_table("movimento_estoque"):
                try:
                    conn.execute(text(
                        "ALTER TABLE `movimento_estoque` "
                        "MODIFY `criado_em` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;"
                    ))
                    print("ALTER movimento_estoque.criado_em aplicado (ou já estava correto).")
                except SQLAlchemyError:
                    pass

            # Garantia do email=191 + UNIQUE sem estourar 767 bytes
            if insp.has_table("usuario"):
                # reduz para 191 se estiver maior
                try:
                    conn.execute(text(
                        "ALTER TABLE `usuario` MODIFY `email` VARCHAR(191) NOT NULL;"
                    ))
                except SQLAlchemyError:
                    pass
                # cria UNIQUE se não existir (ignore erro se já existir)
                try:
                    conn.execute(text(
                        "ALTER TABLE `usuario` ADD UNIQUE `uq_usuario_email` (`email`);"
                    ))
                except SQLAlchemyError:
                    pass
    finally:
        eng.dispose()

if __name__ == "__main__":
    ensure_database()
    create_missing_tables()   # cria primeiro
    apply_alters_if_needed()  # depois altera (se necessário)
    print("✅ reset_schema_safe concluído.")