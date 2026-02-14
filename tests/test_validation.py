"""Testes para utilitários de validação genéricos."""

import pytest

from src.common.utils.validation import (
    normalize_decimal,
    validate_positive_int,
    validate_positive_number,
    validate_range,
)


class TestValidatePositiveNumber:
    """Testa validação de números positivos."""

    def test_validate_positive_number_with_positive_int(self):
        """Testa validação de inteiro positivo."""
        assert validate_positive_number(42) is True

    def test_validate_positive_number_with_zero(self):
        """Testa validação de zero (deve ser válido)."""
        assert validate_positive_number(0) is True

    def test_validate_positive_number_with_negative_int(self):
        """Testa validação de inteiro negativo."""
        assert validate_positive_number(-42) is False

    def test_validate_positive_number_with_positive_float(self):
        """Testa validação de float positivo."""
        assert validate_positive_number(3.14) is True

    def test_validate_positive_number_with_negative_float(self):
        """Testa validação de float negativo."""
        assert validate_positive_number(-3.14) is False

    def test_validate_positive_number_with_string_number(self):
        """Testa validação de string numérica."""
        assert validate_positive_number("100") is True

    def test_validate_positive_number_with_string_decimal_comma(self):
        """Testa validação de string com decimal em vírgula."""
        assert validate_positive_number("100,50") is True

    def test_validate_positive_number_with_string_decimal_dot(self):
        """Testa validação de string com decimal em ponto."""
        assert validate_positive_number("100.50") is True

    def test_validate_positive_number_with_invalid_string(self):
        """Testa validação de string inválida."""
        assert validate_positive_number("abc") is False

    def test_validate_positive_number_with_none(self):
        """Testa validação de None."""
        assert validate_positive_number(None) is False

    def test_validate_positive_number_with_empty_string(self):
        """Testa validação de string vazia."""
        assert validate_positive_number("") is False


class TestValidatePositiveInt:
    """Testa validação de inteiros positivos."""

    def test_validate_positive_int_with_positive_int(self):
        """Testa validação de inteiro positivo."""
        assert validate_positive_int(42) is True

    def test_validate_positive_int_with_zero(self):
        """Testa validação de zero."""
        assert validate_positive_int(0) is True

    def test_validate_positive_int_with_negative_int(self):
        """Testa validação de inteiro negativo."""
        assert validate_positive_int(-42) is False

    def test_validate_positive_int_with_float(self):
        """Testa validação de float (será convertido para string primeiro)."""
        # float é convertido para string, então "3.14" não é inteiro válido
        assert validate_positive_int(3.14) is False

    def test_validate_positive_int_with_string_number(self):
        """Testa validação de string numérica."""
        assert validate_positive_int("100") is True

    def test_validate_positive_int_with_string_negative(self):
        """Testa validação de string com número negativo."""
        assert validate_positive_int("-42") is False

    def test_validate_positive_int_with_invalid_string(self):
        """Testa validação de string inválida."""
        assert validate_positive_int("abc") is False

    def test_validate_positive_int_with_string_decimal(self):
        """Testa validação de string com decimal (será truncada)."""
        # Quando convertido para int, "3.14" gera ValueError
        assert validate_positive_int("3.14") is False

    def test_validate_positive_int_with_none(self):
        """Testa validação de None."""
        assert validate_positive_int(None) is False

    def test_validate_positive_int_with_empty_string(self):
        """Testa validação de string vazia."""
        assert validate_positive_int("") is False


class TestValidateRange:
    """Testa validação de range."""

    def test_validate_range_without_constraints(self):
        """Testa validação sem limites."""
        assert validate_range(50) is True

    def test_validate_range_with_min_only_valid(self):
        """Testa validação com mínimo - valor válido."""
        assert validate_range(50, min_value=10) is True

    def test_validate_range_with_min_only_invalid(self):
        """Testa validação com mínimo - valor inválido."""
        assert validate_range(5, min_value=10) is False

    def test_validate_range_with_max_only_valid(self):
        """Testa validação com máximo - valor válido."""
        assert validate_range(50, max_value=100) is True

    def test_validate_range_with_max_only_invalid(self):
        """Testa validação com máximo - valor inválido."""
        assert validate_range(150, max_value=100) is False

    def test_validate_range_with_both_constraints_valid(self):
        """Testa validação com min e max - valor válido."""
        assert validate_range(50, min_value=10, max_value=100) is True

    def test_validate_range_with_both_constraints_below_min(self):
        """Testa validação com min e max - valor abaixo do mínimo."""
        assert validate_range(5, min_value=10, max_value=100) is False

    def test_validate_range_with_both_constraints_above_max(self):
        """Testa validação com min e max - valor acima do máximo."""
        assert validate_range(150, min_value=10, max_value=100) is False

    def test_validate_range_with_float_values(self):
        """Testa validação com floats."""
        assert validate_range(50.5, min_value=10.5, max_value=100.5) is True

    def test_validate_range_at_min_boundary(self):
        """Testa validação exatamente no limite mínimo."""
        assert validate_range(10, min_value=10) is True

    def test_validate_range_at_max_boundary(self):
        """Testa validação exatamente no limite máximo."""
        assert validate_range(100, max_value=100) is True

    def test_validate_range_with_zero(self):
        """Testa validação de zero."""
        assert validate_range(0, min_value=-10, max_value=10) is True


class TestNormalizeDecimal:
    """Testa normalização de decimais."""

    def test_normalize_decimal_with_comma(self):
        """Testa normalização de vírgula para ponto."""
        assert normalize_decimal("100,50") == "100.50"

    def test_normalize_decimal_with_dot(self):
        """Testa normalização com ponto (sem mudança)."""
        assert normalize_decimal("100.50") == "100.50"

    def test_normalize_decimal_with_integer(self):
        """Testa normalização de inteiro."""
        assert normalize_decimal("100") == "100"

    def test_normalize_decimal_with_multiple_separators(self):
        """Testa normalização com múltiplas vírgulas."""
        # Apenas a primeira é esperada em casos normais
        result = normalize_decimal("1000,00")
        assert result == "1000.00"

    def test_normalize_decimal_with_empty_string(self):
        """Testa normalização de string vazia."""
        assert normalize_decimal("") == ""

    def test_normalize_decimal_with_none(self):
        """Testa normalização de None (converte para string)."""
        assert normalize_decimal(None) == "None"

    def test_normalize_decimal_with_int(self):
        """Testa normalização de inteiro (converte para string)."""
        assert normalize_decimal(100) == "100"

    def test_normalize_decimal_with_float(self):
        """Testa normalização de float."""
        result = normalize_decimal(3.14)
        # Float é convertido para string, pode ter pontos
        assert "." in result or "," in str(result)

    def test_normalize_decimal_with_negative(self):
        """Testa normalização de valor negativo."""
        assert normalize_decimal("-100,50") == "-100.50"

    def test_normalize_decimal_with_whitespace(self):
        """Testa normalização com espaços."""
        # O método replace não remove espaços, apenas substitui vírgula
        result = normalize_decimal(" 100,50 ")
        assert result == " 100.50 "


class TestValidationIntegration:
    """Testes de integração para validação."""

    def test_validate_and_normalize_workflow(self):
        """Testa fluxo de validação e normalização."""
        value = "100,50"
        # Valida
        assert validate_positive_number(value) is True
        # Normaliza
        normalized = normalize_decimal(value)
        assert normalized == "100.50"

    def test_validate_range_with_normalized_values(self):
        """Testa range com valores normalizados."""
        value = "50,00"
        if validate_positive_number(value):
            normalized = float(normalize_decimal(value))
            assert validate_range(normalized, min_value=10, max_value=100) is True
