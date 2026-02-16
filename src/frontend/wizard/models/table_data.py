"""TableRowData dataclass for Stage 2 table data.

This module defines data structures for wizard Stage 2 (table).
Represents individual rows in the receipts table.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from src.common.constants.enums import TipoDiaAssiduidade


@dataclass
class TableRowData:
    """Mutable data structure for a single table row.

    Represents one day of work with associated receipts and values.

    Attributes:
        dia: Day of month (1-31)
        dia_semana: Day of week name (Segunda, Terça, etc.)
        tipo: Type of day (TRABALHO, FERIAS, FERIADO, etc.)
        recibo_inicio: Starting receipt number for this day
        recibo_fim: Ending receipt number for this day
        ips: Number of IPs processed
        valor_com_iva: Total value including VAT
        locais: Work locations for this day
        km: Kilometers traveled
        motivo: Reason (for absences/holidays)
        periodo: Period (for partial absences)
        observacoes: Additional observations
    """

    dia: int
    dia_semana: str
    tipo: TipoDiaAssiduidade = field(
        default=TipoDiaAssiduidade.TRABALHO
    )
    recibo_inicio: int | None = None
    recibo_fim: int | None = None
    ips: int = 0
    valor_com_iva: Decimal = field(
        default_factory=lambda: Decimal("0")
    )
    locais: str = ""
    km: Decimal = field(default_factory=lambda: Decimal("0"))
    motivo: str = ""
    periodo: str = ""
    observacoes: str = ""

    def __post_init__(self) -> None:
        """Validate row data after initialization."""
        if not 1 <= self.dia <= 31:
            raise ValueError(
                f"dia must be between 1 and 31, got {self.dia}"
            )
        if self.ips < 0:
            raise ValueError(
                f"ips must be non-negative, got {self.ips}"
            )
        if self.valor_com_iva < Decimal("0"):
            raise ValueError(
                "valor_com_iva must be non-negative"
            )
        if self.km < Decimal("0"):
            raise ValueError("km must be non-negative")

        # Validate receipts consistency
        if self.recibo_inicio is not None and self.recibo_fim is not None:
            if self.recibo_fim < self.recibo_inicio:
                raise ValueError(
                    f"recibo_fim ({self.recibo_fim}) must be >= "
                    f"recibo_inicio ({self.recibo_inicio})"
                )

    @property
    def num_recibos(self) -> int:
        """Calculate number of receipts for this day.

        Returns:
            Number of receipts (0 if no receipts)
        """
        if (
            self.recibo_inicio is not None
            and self.recibo_fim is not None
        ):
            return self.recibo_fim - self.recibo_inicio + 1
        return 0

    @property
    def is_work_day(self) -> bool:
        """Check if this is a work day.

        Returns:
            True if tipo is TRABALHO
        """
        return self.tipo == TipoDiaAssiduidade.TRABALHO

    def to_dict(
        self,
    ) -> dict[str, int | str | Decimal | None]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary with all row fields
        """
        return {
            "dia": self.dia,
            "dia_semana": self.dia_semana,
            "tipo": self.tipo.value,
            "recibo_inicio": self.recibo_inicio,
            "recibo_fim": self.recibo_fim,
            "ips": self.ips,
            "valor_com_iva": self.valor_com_iva,
            "locais": self.locais,
            "km": self.km,
            "motivo": self.motivo,
            "periodo": self.periodo,
            "observacoes": self.observacoes,
        }

    @classmethod
    def from_dict(
        cls,
        data: dict[str, int | str | Decimal | float | None],
    ) -> TableRowData:
        """Create TableRowData from dictionary.

        Args:
            data: Dictionary with row fields

        Returns:
            New TableRowData instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If field values are invalid
        """
        # Convert numeric fields to proper types
        valor_iva: int | str | Decimal | float | None = data.get("valor_com_iva", Decimal("0"))
        if isinstance(valor_iva, (float, int)):
            valor_iva = Decimal(str(valor_iva))

        km_val: int | str | Decimal | float | None = data.get("km", Decimal("0"))
        if isinstance(km_val, (float, int)):
            km_val = Decimal(str(km_val))

        # Parse tipo enum
        tipo_str: int | str | Decimal | float | None = data.get("tipo", "trabalho")
        if isinstance(tipo_str, TipoDiaAssiduidade):
            tipo_val: TipoDiaAssiduidade = tipo_str
        else:
            tipo_val = TipoDiaAssiduidade(str(tipo_str))

        return cls(
            dia=int(data["dia"]),
            dia_semana=str(data["dia_semana"]),
            tipo=tipo_val,
            recibo_inicio=(
                int(data["recibo_inicio"])
                if data.get("recibo_inicio") is not None
                else None
            ),
            recibo_fim=(
                int(data["recibo_fim"])
                if data.get("recibo_fim") is not None
                else None
            ),
            ips=int(data.get("ips", 0)),
            valor_com_iva=Decimal(str(valor_iva)),
            locais=str(data.get("locais", "")),
            km=Decimal(str(km_val)),
            motivo=str(data.get("motivo", "")),
            periodo=str(data.get("periodo", "")),
            observacoes=str(data.get("observacoes", "")),
        )
