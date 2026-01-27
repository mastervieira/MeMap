"""Modelo Base, comuns para todos os modelos do projecto MeMap"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum

from sqlalchemy import JSON, DateTime, Integer, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

Base = declarative_base()


# =============================================================================
# ENUMS
# =============================================================================


class UserRole(str, Enum):
    """Papel do utilizador no sistema."""

    ADMIN = "ADMIN"  # Acesso total, BD Central, pode aprovar valores
    TECNICO = "TECNICO"  # Acesso normal, BD Distribuição


class ModoBD(str, Enum):
    """Modo de operação da base de dados."""

    CENTRAL = "CENTRAL"  # BD principal (Bruno) - detecta, aprova, exporta
    DISTRIBUICAO = "DISTRIBUICAO"  # BD técnicos - só importa updates


class EstadoDocumento(str, Enum):
    """Estado do documento/mapa."""

    RASCUNHO = "rascunho"  # Em edição no wizard
    ABERTO = "aberto"  # Finalizado mas editável
    FECHADO = "fechado"  # Fechado, read-only


class TipoDiaAssiduidade(str, Enum):
    """Tipo de dia no Mapa de Assiduidade."""

    TRABALHO = "trabalho"
    SABADO = "sabado"
    DOMINGO = "domingo"
    FERIADO = "feriado"
    AUSENCIA = "ausencia"
    FERIAS = "ferias"


# =============================================================================
# MIXIN BASE - Campos comuns a todos os Mapas
# =============================================================================


class MapaBaseMixin:
    """Mixin com campos comuns a todos os Mapas.

    Fornece:
    - Identificação (mes, ano)
    - Estados (rascunho → aberto → fechado)
    - Versionamento
    - Caminhos PDF
    - Timestamps
    - Auditoria em texto

    Nota: tecnico_id será adicionado,
    quando o sistema de users estiver implementado.
    """

    mes: Mapped[int] = mapped_column(Integer, nullable=False)
    ano: Mapped[int] = mapped_column(Integer, nullable=False)

    # Estado do documento
    estado: Mapped[EstadoDocumento] = mapped_column(
        SQLEnum(EstadoDocumento),
        default=EstadoDocumento.RASCUNHO,
        nullable=False,
    )

    # Versionamento (incrementa a cada edição após fecho)
    versao: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    # Caminho do PDF gerado
    pdf_path: Mapped[str | None] = mapped_column(String(500), nullable=False)
    # Dados brutos do wizard (JSON) - para rascunhos
    wizard_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

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
    finalizado_em: Mapped[DateTime] = mapped_column(DateTime, nullable=True)
    fechado_em: Mapped[DateTime] = mapped_column(DateTime, nullable=True)

    # Auditoria em texto (campo no documento)
    # Formato: "1) correção do valor X; 2) alteração do campo Y"
    audit_log: Mapped[str] = mapped_column(Text, nullable=True)

    # Contador de reaberturas
    reopen_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )
