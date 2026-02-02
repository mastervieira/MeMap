from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    false,
    text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base_mixin import Base, MapaBaseMixin, UserRole

# =============================================================================
# USER
# =============================================================================


class User(Base):
    """Utilizador do sistema.

    Campos:
        role: admin (BD Central) ou tecnico (BD Distribuição)
        modo_bd: central (detecta/aprova/exporta) ou distribuicao (só importa)
        ativo: permite desactivar utilizador sem eliminar
        ultimo_login: timestamp do último login bem-sucedido
        nome_completo: opcional, para exibição
        features_enabled: lista de features habilitadas (ex: ["personal_finance"])
    """

    __tablename__ = "users"

    ip: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    username: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False
    )
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)

    modo_bd: Mapped[Enum] = mapped_column(
        SQLEnum(UserRole), default=UserRole.TECNICO, nullable=False
    )
    ativo: Mapped[bool] = mapped_column(default=True, server_default=text("1"))
    ultimo_login: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    nome_completo: Mapped[str] = mapped_column(String(128), nullable=True)

    # Timestamps
    created_at: Mapped[DateTime | None] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relacionamentos com mapas serão adicionados quando tecnico_id for implementado
    # mapas_taxas = relationship("MapaTaxas", back_populates="tecnico")
    # mapas_assiduidade = relationship("MapaAssiduidade", back_populates="tecnico")
    # mapas_contas = relationship("MapaConta", back_populates="tecnico")

    pf_documentos: Mapped[list["Documento"]] = relationship(
        "src.db.models.mapas.Documento",
        back_populates="user", cascade="all, delete-orphan"
    )
