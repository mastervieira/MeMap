from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy import JSON, ForeignKey, Index, Numeric, String, Text, text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_mixin import Base, MapaBaseMixin, TipoDiaAssiduidade
from .user import User


class Documento(Base):
    """Documento anexado (fatura PDF, recibo, extrato bancário).

    Armazena metadata de documentos fiscais com hash para integridade
    e detecção de duplicados.

    Attributes:
        id: Identificador único
        nome_original: Nome do ficheiro original
        path_relativo: Caminho relativo ao diretório de dados
        hash_sha256: Hash do conteúdo para integrity check
        tipo: Tipo de documento (PDF, JPEG, PNG)
        tamanho_bytes: Tamanho do ficheiro
        status_validacao: Estado de validação (VALIDADO, PARCIAL, etc.)
        confianca_score: Score 0-100 da validação automática
        user_id: Utilizador dono do documento
    """

    __tablename__ = "pf_documentos"

    # Primary Key
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Metadata do ficheiro
    nome_original: Mapped[str] = mapped_column(String(255))
    path_relativo: Mapped[str] = mapped_column(String(500))
    hash_sha256: Mapped[str] = mapped_column(String(64), unique=True)

    # Tipo e tamanho
    tipo: Mapped[str] = mapped_column(String(10))
    tamanho_bytes: Mapped[int] = mapped_column()

    # Validação
    status_validacao: Mapped[str] = mapped_column(
        String(20), default="PENDENTE", server_default=text("'PENDENTE'")
    )
    confianca_score: Mapped[int] = mapped_column(
        default=0, server_default=text("0")
    )

    # Dados extraídos (JSON)
    # Usamos Optional porque nullable=True
    dados_extraidos: Mapped[dict[str, Any] | None] = mapped_column(JSON)

    # Foreign Key
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    # Timestamps (v2 recomenda usar utcnow via DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        server_default=text("(CURRENT_TIMESTAMP)"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=text("(CURRENT_TIMESTAMP)"),
    )

    # Relationships
    user: Mapped["User"] = relationship(back_populates="pf_documentos")

    # Índices (Sintaxe de __table_args__ mantém-se igual)
    __table_args__ = (
        Index("idx_pf_documento_hash", "hash_sha256"),
        Index("idx_pf_documento_user", "user_id"),
        Index("idx_pf_documento_status", "status_validacao"),
    )

    def __repr__(self) -> str:
        return f"<Documento(id={self.id}, nome='{self.nome_original}', \
            status='{self.status_validacao}')>"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "nome_original": self.nome_original,
            "tipo": self.tipo,
            "tamanho_kb": round(self.tamanho_bytes / 1024, 2),
            "status_validacao": self.status_validacao,
            "confianca_score": self.confianca_score,
        }


# =============================================================================
# MAPA DE TAXAS
# =============================================================================


class MapaTaxas(MapaBaseMixin, Base):
    """Mapa de Taxas - Listagem de recibos por distrito.

    Dados origem: Stage 2 do Wizard (flat por recibo)
    Optimizado para impressão A4.
    """

    __tablename__ = "mapas_taxas"

    id: Mapped[int] = mapped_column(primary_key=True)

    # tecnico_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # tecnico: Mapped["User"] = relationship(back_populates="mapas_taxas")

    linhas: Mapped[list["MapaTaxasLinha"]] = relationship(
        "MapaTaxasLinha",
        back_populates="mapa",
        cascade="all, delete-orphan",
        order_by="MapaTaxasLinha.ordem",
    )

    # Totais com Numeric (usamos Decimal para tipagem)
    total_setubal: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )
    total_santarem: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )
    total_evora: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )
    total_ips: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    total_dividas: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )
    total_faturacao: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )

    def __repr__(self) -> str:
        return f"<MapaTaxas {self.mes}/{self.ano} estado={self.estado.value}>"

    def calcular_totais(self) -> None:
        self.total_setubal = sum(
            (l.setubal for l in self.linhas), Decimal(0)
        )  # noqa: E741
        self.total_santarem = sum(
            (l.santarem for l in self.linhas), Decimal(0)  # noqa: E741
        )
        self.total_evora = sum(
            (l.evora for l in self.linhas), Decimal(0)
        )  # noqa: E741
        self.total_ips = sum(l.ips for l in self.linhas)  # noqa: E741
        self.total_dividas = sum(
            (l.dividas for l in self.linhas), Decimal(0)
        )  # noqa: E741
        self.total_faturacao = (
            self.total_setubal + self.total_santarem + self.total_evora
        )


class MapaTaxasLinha(Base):
    """Linha do Mapa de Taxas - Um recibo."""

    __tablename__ = "mapas_taxas_linhas"

    id: Mapped[int] = mapped_column(primary_key=True)
    mapa_id: Mapped[int] = mapped_column(
        ForeignKey("mapas_taxas.id", ondelete="CASCADE")
    )

    mapa: Mapped["MapaTaxas"] = relationship(back_populates="linhas")

    ordem: Mapped[int] = mapped_column()
    recibo: Mapped[int] = mapped_column()

    setubal: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    santarem: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    evora: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    ips: Mapped[int] = mapped_column(default=0)
    dividas: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=0)
    dia_origem: Mapped[Optional[int]] = mapped_column()

    @property
    def total_faturacao(self) -> Decimal:
        return self.setubal + self.santarem + self.evora


# =============================================================================
# MAPA DE ASSIDUIDADE
# =============================================================================


class MapaAssiduidade(MapaBaseMixin, Base):
    """Mapa de Assiduidade - Registo diário de trabalho.

    Dados origem: Stage 1 (dias especiais) + Stage 2 (lançamentos)
    Mostra TODOS os dias do mês com marca d'água para FDS/Feriados.
    Optimizado para impressão A4.
    """

    __tablename__ = "mapas_assiduidade"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Campos obrigatórios herdados de MapaBaseMixin
    # mes: Mapped[int] = mapped_column()
    # ano: Mapped[int] = mapped_column()
    # estado: Mapped[EstadoDocumento] = mapped_column()
    # versao: Mapped[int] = mapped_column(default=1)
    # wizard_data: Mapped[dict[str, Any] | None] = mapped_column(JSON)
    # created_at: Mapped[datetime] = mapped_column()
    # updated_at: Mapped[datetime] = mapped_column()
    # pdf_path: Mapped[str | None] = mapped_column(String(500))
    # finalizado_em: Mapped[datetime | None] = mapped_column()
    # fechado_em: Mapped[datetime | None] = mapped_column()

    linhas: Mapped[list["MapaAssiduidadeLinha"]] = relationship(
        back_populates="mapa",
        cascade="all, delete-orphan",
        order_by="MapaAssiduidadeLinha.dia",
    )

    # Totais calculados
    total_dias_trabalho: Mapped[int] = mapped_column(
        default=0, server_default=text("0")
    )
    total_km: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )
    total_ips: Mapped[int] = mapped_column(default=0, server_default=text("0"))
    total_faturacao: Mapped[Decimal] = mapped_column(
        Numeric(10, 2), default=0, server_default=text("0")
    )
    total_ausencias: Mapped[int] = mapped_column(
        default=0, server_default=text("0")
    )
    total_ferias: Mapped[int] = mapped_column(
        default=0, server_default=text("0")
    )
    total_feriados: Mapped[int] = mapped_column(
        default=0, server_default=text("0")
    )

    def __repr__(self) -> str:
        return f"<MapaAssiduidade {self.mes}/{self.ano} estado={self.estado.value}>"


class MapaAssiduidadeLinha(Base):
    __tablename__ = "mapas_assiduidade_linhas"

    id: Mapped[int] = mapped_column(primary_key=True)
    mapa_id: Mapped[int] = mapped_column(
        ForeignKey("mapas_assiduidade.id", ondelete="CASCADE")
    )

    mapa: Mapped["MapaAssiduidade"] = relationship(back_populates="linhas")

    dia: Mapped[int] = mapped_column()
    dia_semana: Mapped[str] = mapped_column(String(20))
    tipo: Mapped[TipoDiaAssiduidade] = mapped_column(
        SQLEnum(TipoDiaAssiduidade), default=TipoDiaAssiduidade.TRABALHO
    )

    # Campos opcionais (nullable=True por defeito no Mapped[Optional])
    recibo_inicio: Mapped[Optional[int]] = mapped_column()
    recibo_fim: Mapped[Optional[int]] = mapped_column()
    ips: Mapped[Optional[int]] = mapped_column(default=0)
    valor_sem_iva: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(10, 2), default=0
    )
    locais: Mapped[Optional[str]] = mapped_column(String(200))
    km: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), default=0)
    motivo: Mapped[Optional[str]] = mapped_column(String(200))
    periodo: Mapped[Optional[str]] = mapped_column(String(20))
    observacoes: Mapped[Optional[str]] = mapped_column(Text)
