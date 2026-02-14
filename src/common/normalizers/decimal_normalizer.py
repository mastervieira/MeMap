"""
Normalizador de valores decimais.
Converte separadores decimais entre ponto e vírgula.
"""


def normalize_decimal(value: str) -> str:
    """Normaliza valor decimal para usar vírgula como separador.

    Aceita tanto ponto quanto vírgula e normaliza para vírgula.
    Remove espaços em branco.

    Args:
        value: String com valor numérico

    Returns:
        String normalizada com vírgula como separador decimal

    Examples:
        >>> normalize_decimal("10.5")
        "10,5"
        >>> normalize_decimal("10,5")
        "10,5"
        >>> normalize_decimal(" 10.5 ")
        "10,5"
    """
    if not value:
        return "0"

    # Remove espaços
    normalized: str = value.strip()

    # Substitui ponto por vírgula
    normalized = normalized.replace(".", ",")

    return normalized


def decimal_to_float(value: str) -> float:
    """Converte string decimal (com vírgula ou ponto) para float.

    Args:
        value: String com valor numérico

    Returns:
        Valor como float

    Raises:
        ValueError: Se o valor não puder ser convertido

    Examples:
        >>> decimal_to_float("10,5")
        10.5
        >>> decimal_to_float("10.5")
        10.5
    """
    if not value:
        return 0.0

    # Remove espaços e converte vírgula para ponto para conversão
    cleaned: str = value.strip().replace(",", ".")

    try:
        return float(cleaned)
    except ValueError as e:
        raise ValueError(f"Valor inválido para conversão: {value}") from e


def format_currency(value: float, symbol: str = "€") -> str:
    """Formata valor como moeda com 2 casas decimais.

    Args:
        value: Valor numérico
        symbol: Símbolo da moeda (padrão: €)

    Returns:
        String formatada como moeda

    Examples:
        >>> format_currency(10.5)
        "10,50 €"
        >>> format_currency(1234.56)
        "1234,56 €"
    """
    formatted: str = f"{value:.2f}".replace(".", ",")
    return f"{formatted} {symbol}"
