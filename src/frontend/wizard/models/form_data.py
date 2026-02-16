"""FormData dataclass for Stage 1 form data.

This module defines the data structure for wizard Stage 1 (form).
Contains all fields from the initial wizard form page.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(frozen=True)
class FormData:
    """Immutable data structure for wizard Stage 1 form.

    Attributes:
        quantidade_recibos: Number of receipts to process
        recibo_inicio: Starting receipt number
        recibo_fim: Ending receipt number
        zona_primaria: Primary work zone (Setúbal/Santarém/Évora)
        zona_secundaria: Secondary work zone
        total_km: Total kilometers traveled
    """

    quantidade_recibos: int
    recibo_inicio: int
    recibo_fim: int
    zona_primaria: str
    zona_secundaria: str
    total_km: Decimal = field(default_factory=lambda: Decimal("0"))

    def __post_init__(self) -> None:
        """Validate form data after initialization."""
        if self.quantidade_recibos < 0:
            raise ValueError(
                "quantidade_recibos must be non-negative"
            )
        if self.recibo_inicio < 0:
            raise ValueError("recibo_inicio must be non-negative")
        if self.recibo_fim < 0:
            raise ValueError("recibo_fim must be non-negative")
        if self.recibo_fim < self.recibo_inicio:
            raise ValueError(
                "recibo_fim must be >= recibo_inicio"
            )
        if self.total_km < Decimal("0"):
            raise ValueError("total_km must be non-negative")

        # Validate consistency
        expected_qty: int = self.recibo_fim - self.recibo_inicio + 1
        if self.quantidade_recibos != expected_qty:
            raise ValueError(
                f"quantidade_recibos ({self.quantidade_recibos}) "
                f"does not match range ({expected_qty})"
            )

    def to_dict(self) -> dict[str, int | str | Decimal]:
        """Convert to dictionary for serialization.

        Returns:
            Dictionary with all form fields
        """
        return {
            "quantidade_recibos": self.quantidade_recibos,
            "recibo_inicio": self.recibo_inicio,
            "recibo_fim": self.recibo_fim,
            "zona_primaria": self.zona_primaria,
            "zona_secundaria": self.zona_secundaria,
            "total_km": self.total_km,
        }

    @classmethod
    def from_dict(
        cls, data: dict[str, int | str | Decimal | float]
    ) -> FormData:
        """Create FormData from dictionary.

        Args:
            data: Dictionary with form fields

        Returns:
            New FormData instance

        Raises:
            KeyError: If required fields are missing
            ValueError: If field values are invalid
        """
        # Convert total_km to Decimal if it's float
        total_km_val: int | str | Decimal | float = data.get("total_km", Decimal("0"))
        if isinstance(total_km_val, (float, int)):
            total_km_val = Decimal(str(total_km_val))

        return cls(
            quantidade_recibos=int(data["quantidade_recibos"]),
            recibo_inicio=int(data["recibo_inicio"]),
            recibo_fim=int(data["recibo_fim"]),
            zona_primaria=str(data["zona_primaria"]),
            zona_secundaria=str(data["zona_secundaria"]),
            total_km=Decimal(str(total_km_val)),
        )
