"""
Utilitários de validação genéricos para o projeto MeMap Pro.
Funções auxiliares reutilizáveis para validação de dados.
"""



def validate_positive_number(value: float | int) -> bool:
    """Valida se um valor pode ser convertido para número positivo.

    Args:
        value: Valor a validar

    Returns:
        True se é número positivo, False caso contrário
    """
    try:
        return float(str(value).replace(",", ".")) >= 0
    except (ValueError, TypeError, AttributeError):
        return False


def validate_positive_int(value: int) -> bool:
    """Valida se um valor pode ser convertido para inteiro positivo.

    Args:
        value: Valor a validar

    Returns:
        True se é inteiro positivo, False caso contrário
    """
    try:
        num = int(str(value))
        return num >= 0
    except (ValueError, TypeError, AttributeError):
        return False


def validate_range(
    value: float | int,
    min_value: float | int | None = None,
    max_value: float | int | None = None
) -> bool:
    """Valida se um valor está dentro de um range.

    Args:
        value: Valor numérico a validar
        min_value: Valor mínimo permitido (opcional)
        max_value: Valor máximo permitido (opcional)

    Returns:
        True se está no range, False caso contrário
    """
    if min_value is not None and value < min_value:
        return False
    if max_value is not None and value > max_value:
        return False
    return True


def normalize_decimal(value: str) -> str:
    """Normaliza separador decimal de vírgula para ponto.

    Args:
        value: String com número

    Returns:
        String com ponto decimal
    """
    return str(value).replace(",", ".")
