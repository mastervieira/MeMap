"""
Validador genérico para formulários do MeMap Pro.
Fornece validação tipada e segura para dados de formulários.
"""

from dataclasses import dataclass
from typing import Any, TypedDict

from src.common.utils.validation import (
    normalize_decimal,
    validate_positive_int,
    validate_positive_number,
)


@dataclass(frozen=True)
class ValidationResult:
    """Resultado imutável de uma operação de validação."""
    is_valid: bool
    data: dict[str, Any] | None = None
    error_message: str | None = None


class BaseFormValidator:
    """Validador base para formulários."""

    def __init__(self) -> None:
        self.errors: list[str] = []

    def add_error(self, error: str) -> None:
        """Adiciona um erro à lista de erros."""
        self.errors.append(error)

    def clear_errors(self) -> None:
        """Limpa todos os erros."""
        self.errors = []

    def has_errors(self) -> bool:
        """Verifica se há erros."""
        return len(self.errors) > 0


def safe_int_convert(value: Any) -> int | None:
    """Converte valor para int de forma segura.

    Args:
        value: Valor a converter

    Returns:
        Inteiro convertido ou None se falhar
    """
    try:
        return int(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def safe_float_convert(value: Any) -> float | None:
    """Converte valor para float de forma segura.

    Args:
        value: Valor a converter

    Returns:
        Float convertido ou None se falhar
    """
    try:
        return float(normalize_decimal(str(value)))
    except (ValueError, TypeError, AttributeError):
        return None
