# estoque/services.py (substitua completo, se preferir)
from __future__ import annotations
from contextlib import contextmanager
from typing import Optional, List
import re
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from .db import SessionLocal
from .models import (
    Empresa, Usuario, Produto, MovimentoEstoque,
    TipoUsuario, TipoMov
)
from .security import hash_password, verify_password

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@contextmanager
def get_session() -> Session:
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

# ---- Utilitários de validação ----
def _validar_email(email: str):
    if not EMAIL_RE.match(email or ""):
        raise ValueError("Email inválido.")

def _validar_senha(s: str):
    if not s or len(s) < 6:
        raise ValueError("A senha deve ter ao menos 6 caracteres.")

def _limpar_cnpj(cnpj: str) -> str:
    return "".join(ch for ch in (cnpj or "") if ch.isdigit())

def _validar_cnpj_simples(cnpj: str):
    c = _limpar_cnpj(cnpj)
    if len(c) != 14:
        raise ValueError("CNPJ deve ter 14 dígitos (apenas números).")
    return c

# ---- Auth ----
def autenticar(email: str, senha: str) -> Optional[Usuario]:
    with get_session() as db:
        user = db.scalar(select(Usuario).where(Usuario.email == email))
        if user and verify_password(senha, user.senha_hash):
            return user
        return None

# ---- Empresas ----
def listar_empresas() -> List[Empresa]:
    with get_session() as db:
        stmt = select(Empresa).order_by(Empresa.nome)
        return list(db.scalars(stmt))

def criar_empresa(admin: Usuario, nome: str, cnpj: str, telefone: Optional[str] = None) -> Empresa:
    if admin.tipo != TipoUsuario.ADMIN:
        raise PermissionError("Ação permitida apenas para Admin.")

    if not (nome or "").strip():
        raise ValueError("Nome da empresa é obrigatório.")
    c = _validar_cnpj_simples(cnpj)

    with get_session() as db:
        try:
            e = Empresa(nome=nome.strip(), cnpj=c, telefone=(telefone or "").strip() or None)
            db.add(e)
            db.flush()
            return e
        except IntegrityError:
            raise ValueError("CNPJ já cadastrado.")

# ---- Usuários ----
def criar_usuario(admin: Usuario, nome: str, email: str, senha_plana: str,
                  tipo: TipoUsuario, empresa_id: Optional[int]) -> Usuario:
    if admin.tipo != TipoUsuario.ADMIN:
        raise PermissionError("Ação permitida apenas para Admin.")

    if not (nome or "").strip():
        raise ValueError("Nome do usuário é obrigatório.")
    _validar_email(email)
    _validar_senha(senha_plana)

    if tipo == TipoUsuario.PADRAO and not empresa_id:
        raise ValueError("Usuário Padrão deve estar vinculado a uma empresa.")

    with get_session() as db:
        if empresa_id and not db.get(Empresa, empresa_id):
            raise ValueError("Empresa não encontrada.")
        try:
            u = Usuario(
                nome=nome.strip(), email=email.strip(),
                senha_hash=hash_password(senha_plana),
                tipo=tipo, empresa_id=empresa_id
            )
            db.add(u)
            db.flush()
            return u
        except IntegrityError:
            raise ValueError("Email já cadastrado.")

# ---- Produtos ----
def criar_produto(user: Usuario, empresa_id: int, codigo: str, descricao: str,
                  minimo_estoque: Optional[int] = None) -> Produto:
    if user.tipo != TipoUsuario.ADMIN and user.empresa_id != empresa_id:
        raise PermissionError("Acesso negado para outra empresa.")

    codigo = (codigo or "").strip()
    descricao = (descricao or "").strip()
    if not codigo:
        raise ValueError("Código do produto é obrigatório.")
    if not descricao:
        raise ValueError("Descrição do produto é obrigatória.")

    with get_session() as db:
        if not db.get(Empresa, empresa_id):
            raise ValueError("Empresa não encontrada.")
        try:
            p = Produto(
                empresa_id=empresa_id, codigo=codigo,
                descricao=descricao, minimo_estoque=minimo_estoque,
                estoque=0, ativo=True
            )
            db.add(p)
            db.flush()
            return p
        except IntegrityError:
            raise ValueError("Já existe um produto com este código nesta empresa.")

def listar_produtos(user: Usuario) -> List[Produto]:
    if not user.empresa_id and user.tipo != TipoUsuario.ADMIN:
        raise PermissionError("Usuário sem empresa.")
    with get_session() as db:
        stmt = select(Produto).where(Produto.empresa_id == user.empresa_id).order_by(Produto.descricao)
        return list(db.scalars(stmt))

# ---- Movimentos ----
def lancar_movimento(user: Usuario, produto_id: int, tipo: TipoMov, quantidade: int,
                     custo_unitario: Optional[float] = None, observacao: Optional[str] = None) -> MovimentoEstoque:
    if not isinstance(quantidade, int) or quantidade <= 0:
        raise ValueError("Quantidade deve ser um inteiro positivo.")

    with get_session() as db:
        prod = db.get(Produto, produto_id)
        if not prod or not prod.ativo:
            raise ValueError("Produto inexistente ou inativo.")
        if user.tipo != TipoUsuario.ADMIN and user.empresa_id != prod.empresa_id:
            raise PermissionError("Acesso negado para outra empresa.")

        # Soma/Subtrai estoque
        novo = prod.estoque + quantidade if tipo == TipoMov.ENTRADA else prod.estoque - quantidade
        if novo < 0:
            raise ValueError("Saldo insuficiente para saída.")

        prod.estoque = novo
        mov = MovimentoEstoque(
            empresa_id=prod.empresa_id,
            produto_id=prod.id,
            tipo=tipo,
            quantidade=quantidade,
            custo_unitario=custo_unitario,
            criado_por_id=user.id,
            observacao=(observacao or "").strip() or None,
        )
        db.add(mov)
        db.flush()
        return mov

def listar_movimentos(user: Usuario) -> List[MovimentoEstoque]:
    with get_session() as db:
        stmt = select(MovimentoEstoque).where(MovimentoEstoque.empresa_id == user.empresa_id).order_by(MovimentoEstoque.criado_em.desc())
        return list(db.scalars(stmt))
    
# estoque/services.py  (ADICIONAR ESTES MÉTODOS)

from sqlalchemy import select

def obter_produto(produto_id: int) -> Produto | None:
    with get_session() as db:
        return db.get(Produto, produto_id)

def get_nome_produto(produto_id: int) -> str | None:
    with get_session() as db:
        p = db.get(Produto, produto_id)
        return p.descricao if p else None   

def produto_em_alerta(produto_id: int) -> bool:
    with get_session() as db:
        p = db.get(Produto, produto_id)
        if not p:
            return False
        if p.minimo_estoque is None:
            return False
        return p.estoque <= p.minimo_estoque

def produtos_criticos(user: Usuario) -> list[Produto]:
    """Lista produtos da empresa do usuário com estoque <= mínimo."""
    if not user or not user.empresa_id:
        return []
    with get_session() as db:
        stmt = (
            select(Produto)
            .where(
                Produto.empresa_id == user.empresa_id,
                Produto.minimo_estoque.is_not(None),
                Produto.estoque <= Produto.minimo_estoque,
            )
            .order_by(Produto.descricao)
        )
        return list(db.scalars(stmt))
