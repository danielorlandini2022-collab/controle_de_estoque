from __future__ import annotations
from datetime import datetime
from typing import Optional, List
import enum

from sqlalchemy import (
    String, Integer, Boolean, Enum, DateTime, ForeignKey,
    UniqueConstraint, CheckConstraint, func, TIMESTAMP, text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base

class TipoUsuario(enum.IntEnum):
    PADRAO = 0
    ADMIN = 1

class Empresa(Base):
    __tablename__ = 'empresa'
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(128), nullable=False)
    cnpj: Mapped[str] = mapped_column(String(18), nullable=False, unique=True)
    telefone: Mapped[Optional[str]] = mapped_column(String(32))
    # ❌ era DateTime(server_default=func.now())
    # ✅ use TIMESTAMP com CURRENT_TIMESTAMP (sem aspas)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )

    usuarios: Mapped[List['Usuario']] = relationship(back_populates='empresa', cascade='all, delete-orphan')
    produtos: Mapped[List['Produto']] = relationship(back_populates='empresa', cascade='all, delete-orphan')



class Usuario(Base):
    __tablename__ = 'usuario'

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(191), nullable=False, unique=True, index=True)
    senha_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    tipo: Mapped['TipoUsuario'] = mapped_column(Enum(TipoUsuario), nullable=False, default=TipoUsuario.PADRAO)

    empresa_id: Mapped[Optional[int]] = mapped_column(ForeignKey('empresa.id', ondelete='SET NULL'))
    empresa: Mapped[Optional['Empresa']] = relationship(back_populates='usuarios')

class Produto(Base):
    __tablename__ = 'produto'
    __table_args__ = (
        UniqueConstraint('empresa_id', 'codigo', name='uq_produto_empresa_codigo'),
        CheckConstraint('estoque >= 0', name='ck_estoque_nao_negativo'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo: Mapped[str] = mapped_column(String(64), nullable=False)
    descricao: Mapped[str] = mapped_column(String(191), nullable=False)
    estoque: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    minimo_estoque: Mapped[Optional[int]] = mapped_column(Integer)

    empresa_id: Mapped[int] = mapped_column(ForeignKey('empresa.id', ondelete='CASCADE'), index=True, nullable=False)
    empresa: Mapped['Empresa'] = relationship(back_populates='produtos')

class TipoMov(enum.Enum):
    ENTRADA = 'ENTRADA'
    SAIDA = 'SAIDA'

class MovimentoEstoque(Base):
    __tablename__ = 'movimento_estoque'
    id: Mapped[int] = mapped_column(primary_key=True)
    empresa_id: Mapped[int] = mapped_column(ForeignKey('empresa.id', ondelete='CASCADE'), index=True, nullable=False)
    produto_id: Mapped[int] = mapped_column(ForeignKey('produto.id', ondelete='CASCADE'), index=True, nullable=False)
    tipo: Mapped['TipoMov'] = mapped_column(Enum(TipoMov), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    custo_unitario: Mapped[Optional[float]] = mapped_column()
    criado_por_id: Mapped[Optional[int]] = mapped_column(ForeignKey('usuario.id', ondelete='SET NULL'))
    criado_em: Mapped[datetime] = mapped_column(
        TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"), nullable=False
    )
    observacao: Mapped[Optional[str]] = mapped_column(String(512))
