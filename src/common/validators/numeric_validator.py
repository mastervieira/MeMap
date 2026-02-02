"""Validador para dados numéricos em formulários.

Verifica:
- Tipo de dado (int, float, decimal)
- Range de valores (min/max)
- Casas decimais (precision)
- Caracteres válidos
- Conversão segura de strings para números
- Validação de campos específicos (age, percentage, currency)

Uso:
    from src.common.validators.numeric_validator import NumericValidator

    validator = NumericValidator()
    result = validator.validate_field("age", "25")

    if result.is_valid:
        value = result.converted_value
    else:
        # Mostrar erros
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from ..constants.numeric_constants import (
    ALLOWED_TYPES,
    DEFAULT_MAX_VALUE,
    DEFAULT_MIN_VALUE,
    FIELD_CONFIGS,
    FLOAT_TOLERANCE,
    NUMERIC_TYPES,
)
from .base_validator import BaseValidator

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Resultado da validação de dado numérico."""

    is_valid: bool = True
    field_name: str = ""
    original_value: str | float | int = ""
    converted_value: int | float | Decimal | None = None
    value_type: str = ""
    is_in_range: bool = True
    is_precision_valid: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_warning(self, msg: str) -> None:
        """Adiciona aviso."""
        self.warnings.append(msg)

    def add_error(self, msg: str) -> None:
        """Adiciona erro e marca como inválido."""
        self.errors.append(msg)
        self.is_valid = False


class NumericValidator(BaseValidator):
    """Validador para dados numéricos em formulários."""

    def __init__(self) -> None:
        """Inicializa validador numérico."""
        super().__init__()
        self._validation_result: ValidationResult | None = None

    def is_valid(self, data: dict[str, str | int | float]) -> bool:
        """Valida dicionário com dados numéricos.

        Args:
            data: Dicionário com field_name e value

        Returns:
            True se dados são válidos, False caso contrário
        """
        if not isinstance(data, dict):
            return False

        field_name = data.get("field_name", "")
        value = data.get("value")

        result = self.validate_field(field_name, value)
        self._validation_result = result
        return result.is_valid

    def get_errors(self) -> dict[str, str]:
        """Obtém erros de validação.

        Returns:
            Dicionário com mensagens de erro
        """
        if self._validation_result is None:
            return {}

        errors = {}

        if self._validation_result.errors:
            errors["numeric_field"] = " | ".join(
                self._validation_result.errors
            )

        return errors

    def validate_field(
        self,
        field_name: str,
        value: str | int | float,
        value_type: str = "float",
        min_value: float | None = None,
        max_value: float | None = None,
        decimal_places: int | None = None,
    ) -> ValidationResult:
        """Valida um campo numérico específico.

        Args:
            field_name: Nome do campo
            value: Valor a validar
            value_type: Tipo esperado (int, float, decimal)
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            decimal_places: Número máximo de casas decimais

        Returns:
            ValidationResult com detalhes da validação
        """
        result = ValidationResult(
            field_name=field_name,
            original_value=value,
            value_type=value_type,
        )

        # Verificar se field_name tem configuração predefinida
        if field_name in FIELD_CONFIGS:
            config = FIELD_CONFIGS[field_name]
            min_value = min_value or config.get("min")
            max_value = max_value or config.get("max")
            decimal_places = (
                decimal_places or config.get("decimal_places")
            )

        # 1. Validar tipo
        if not self._validate_type(value_type, result):
            return result

        # 2. Converter valor
        converted = self._convert_value(
            value, value_type, field_name, result
        )
        if converted is None:
            return result

        result.converted_value = converted

        # 3. Validar range
        if min_value is not None or max_value is not None:
            self._validate_range(
                converted, min_value, max_value, result
            )

        # 4. Validar precisão (casas decimais)
        if decimal_places is not None:
            self._validate_precision(converted, decimal_places, result)

        return result

    def validate_multiple(
        self,
        fields: dict[str, dict],
    ) -> dict[str, ValidationResult]:
        """Valida múltiplos campos numéricos.

        Args:
            fields: Dicionário com configuração de campos
                    (value, type, min, max, decimal_places)

        Returns:
            Dicionário com resultados por campo
        """
        results = {}

        for field_name, config in fields.items():
            value = config.get("value")
            value_type = config.get("type", "float")
            min_value = config.get("min")
            max_value = config.get("max")
            decimal_places = config.get("decimal_places")

            results[field_name] = self.validate_field(
                field_name,
                value,
                value_type,
                min_value,
                max_value,
                decimal_places,
            )

        return results

    def _validate_type(
        self, value_type: str, result: ValidationResult
    ) -> bool:
        """Valida se tipo é suportado."""
        if value_type not in ALLOWED_TYPES:
            result.add_error(
                f"Tipo de dado não suportado: {value_type}. "
                f"Permitidos: {', '.join(ALLOWED_TYPES)}"
            )
            return False
        return True

    def _convert_value(
        self,
        value: str | int | float,
        value_type: str,
        field_name: str,
        result: ValidationResult,
    ) -> int | float | Decimal | None:
        """Converte valor para tipo especificado."""
        if value is None:
            result.add_error(f"Campo {field_name} não pode ser vazio")
            return None

        # Se já é número, tratar diretamente
        if isinstance(value, NUMERIC_TYPES):
            return self._handle_numeric_input(
                value, value_type, result
            )

        # Converter string para número
        if not isinstance(value, str):
            result.add_error(
                f"Tipo inválido: {type(value).__name__}. "
                f"Esperado: string ou número"
            )
            return None

        return self._convert_string(
            value.strip(), value_type, result
        )

    def _handle_numeric_input(
        self,
        value: int | float,
        value_type: str,
        result: ValidationResult,
    ) -> int | float | None:
        """Processa input que já é numérico."""
        if value_type == "int" and not isinstance(value, int):
            try:
                return int(value)
            except (ValueError, TypeError):
                result.add_error("Não é possível converter para int")
                return None
        return value

    def _convert_string(
        self,
        value: str,
        value_type: str,
        result: ValidationResult,
    ) -> int | float | Decimal | None:
        """Converte string para tipo numérico."""
        try:
            if value_type == "int":
                return int(value)
            elif value_type == "float":
                return float(value.replace(",", "."))
            elif value_type == "decimal":
                return Decimal(value.replace(",", "."))
            elif value_type == "percentage":
                if value.endswith("%"):
                    value = value[:-1].strip()
                return float(value.replace(",", "."))
            else:
                result.add_error(f"Tipo desconhecido: {value_type}")
                return None
        except (ValueError, InvalidOperation) as e:
            result.add_error(
                f"Não é possível converter '{value}': {e}"
            )
            return None

    def _validate_range(
        self,
        value: int | float | Decimal,
        min_value: float | None,
        max_value: float | None,
        result: ValidationResult,
    ) -> None:
        """Valida se valor está dentro do range."""
        if min_value is None:
            min_value = DEFAULT_MIN_VALUE
        if max_value is None:
            max_value = DEFAULT_MAX_VALUE

        try:
            # Comparação com tolerância para floats
            if isinstance(value, float):
                in_range = (
                    min_value - FLOAT_TOLERANCE
                    <= value
                    <= max_value + FLOAT_TOLERANCE
                )
            else:
                in_range = min_value <= value <= max_value

            if not in_range:
                result.is_in_range = False
                result.add_error(
                    f"Valor {value} fora do range "
                    f"[{min_value}, {max_value}]"
                )

        except Exception as e:
            result.add_error(f"Erro ao validar range: {e}")

    def _validate_precision(
        self,
        value: int | float | Decimal,
        decimal_places: int,
        result: ValidationResult,
    ) -> None:
        """Valida número de casas decimais."""
        if isinstance(value, int):
            return  # Inteiros sempre têm 0 casas decimais

        try:
            str_value = str(value)

            # Encontrar ponto decimal
            if "." in str_value:
                _, decimal_part = str_value.split(".")
                actual_places = len(decimal_part.rstrip("0"))

                if actual_places > decimal_places:
                    result.is_precision_valid = False
                    result.add_error(
                        f"Demasiadas casas decimais: {actual_places} "
                        f"(máximo: {decimal_places})"
                    )

        except Exception as e:
            result.add_error(f"Erro ao validar precisão: {e}")


def validate_numeric_field(
    field_name: str,
    value: str | int | float,
    value_type: str = "float",
    min_value: float | None = None,
    max_value: float | None = None,
) -> dict:
    """Função de conveniência para validar campo numérico.

    Args:
        field_name: Nome do campo
        value: Valor a validar
        value_type: Tipo de dado
        min_value: Valor mínimo
        max_value: Valor máximo

    Returns:
        Dicionário com resultado da validação
    """
    validator = NumericValidator()
    result = validator.validate_field(
        field_name, value, value_type, min_value, max_value
    )
    return {
        "valido": result.is_valid,
        "campo": result.field_name,
        "valor_original": result.original_value,
        "valor_convertido": str(result.converted_value),
        "tipo": result.value_type,
        "dentro_do_range": result.is_in_range,
        "precisao_valida": result.is_precision_valid,
        "avisos": result.warnings,
        "erros": result.errors,
    }
