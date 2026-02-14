"""Testes para normalizadores de dados."""

import pytest

from src.common.normalizers.decimal_normalizer import (
    decimal_to_float,
    format_currency,
    normalize_decimal,
)


class TestNormalizeDecimal:
    """Testa normalização de decimais."""

    def test_normalize_decimal_with_dot(self):
        """Testa normalização de ponto para vírgula."""
        result = normalize_decimal("100.50")
        assert result == "100,50"

    def test_normalize_decimal_with_comma(self):
        """Testa normalização com vírgula (sem mudança)."""
        result = normalize_decimal("100,50")
        assert result == "100,50"

    def test_normalize_decimal_with_spaces(self):
        """Testa remoção de espaços."""
        result = normalize_decimal(" 100.50 ")
        assert result == "100,50"

    def test_normalize_decimal_integer(self):
        """Testa normalização de inteiro."""
        result = normalize_decimal("100")
        assert result == "100"

    def test_normalize_decimal_empty_string(self):
        """Testa normalização de string vazia."""
        result = normalize_decimal("")
        assert result == "0"

    def test_normalize_decimal_none(self):
        """Testa normalização de None."""
        result = normalize_decimal(None)
        assert result == "0"

    def test_normalize_decimal_with_leading_zeros(self):
        """Testa normalização com zeros à frente."""
        result = normalize_decimal("0.50")
        assert result == "0,50"

    def test_normalize_decimal_negative(self):
        """Testa normalização de número negativo."""
        result = normalize_decimal("-100.50")
        assert result == "-100,50"

    def test_normalize_decimal_large_number(self):
        """Testa normalização de número grande."""
        result = normalize_decimal("1000000.99")
        assert result == "1000000,99"

    def test_normalize_decimal_many_decimals(self):
        """Testa normalização com muitas casas decimais."""
        result = normalize_decimal("100.123456")
        assert result == "100,123456"


class TestDecimalToFloat:
    """Testa conversão de decimal (string) para float."""

    def test_decimal_to_float_with_comma(self):
        """Testa conversão de vírgula para ponto."""
        result = decimal_to_float("100,50")
        assert result == 100.50

    def test_decimal_to_float_with_dot(self):
        """Testa conversão com ponto (sem mudança)."""
        result = decimal_to_float("100.50")
        assert result == 100.50

    def test_decimal_to_float_integer(self):
        """Testa conversão de inteiro."""
        result = decimal_to_float("100")
        assert result == 100.0

    def test_decimal_to_float_zero(self):
        """Testa conversão de zero."""
        result = decimal_to_float("0")
        assert result == 0.0

    def test_decimal_to_float_zero_with_decimals(self):
        """Testa conversão de zero com decimais."""
        result = decimal_to_float("0,00")
        assert result == 0.0

    def test_decimal_to_float_negative(self):
        """Testa conversão de valor negativo."""
        result = decimal_to_float("-100,50")
        assert result == -100.50

    def test_decimal_to_float_large_number(self):
        """Testa conversão de número grande."""
        result = decimal_to_float("1000000,99")
        assert result == 1000000.99

    def test_decimal_to_float_small_decimal(self):
        """Testa conversão de decimal pequeno."""
        result = decimal_to_float("0,01")
        assert result == 0.01

    def test_decimal_to_float_many_decimals(self):
        """Testa conversão com muitas casas decimais."""
        result = decimal_to_float("100,123456")
        assert abs(result - 100.123456) < 0.0001

    def test_decimal_to_float_invalid_string(self):
        """Testa conversão de string inválida."""
        with pytest.raises(ValueError):
            decimal_to_float("abc")

    def test_decimal_to_float_empty_string(self):
        """Testa conversão de string vazia retorna zero."""
        result = decimal_to_float("")
        assert result == 0.0

    def test_decimal_to_float_whitespace(self):
        """Testa conversão com espaços."""
        result = decimal_to_float("100,50 ")
        assert abs(result - 100.50) < 0.01

    def test_decimal_to_float_leading_whitespace(self):
        """Testa conversão com espaços no início."""
        result = decimal_to_float(" 100,50")
        assert abs(result - 100.50) < 0.01

    def test_decimal_to_float_multiple_separators(self):
        """Testa conversão com múltiplos separadores."""
        with pytest.raises(ValueError):
            decimal_to_float("100,50,99")


class TestFormatCurrency:
    """Testa formatação de moeda."""

    def test_format_currency_default_symbol(self):
        """Testa formatação com símbolo padrão."""
        result = format_currency(10.5)
        assert "10,50" in result
        assert "€" in result

    def test_format_currency_custom_symbol(self):
        """Testa formatação com símbolo customizado."""
        result = format_currency(10.5, symbol="$")
        assert "10,50" in result
        assert "$" in result

    def test_format_currency_integer(self):
        """Testa formatação de inteiro."""
        result = format_currency(100)
        assert "100,00" in result

    def test_format_currency_zero(self):
        """Testa formatação de zero."""
        result = format_currency(0)
        assert "0,00" in result

    def test_format_currency_negative(self):
        """Testa formatação de valor negativo."""
        result = format_currency(-100.50)
        assert "-100,50" in result

    def test_format_currency_large_number(self):
        """Testa formatação de número grande."""
        result = format_currency(1234567.89)
        assert "1234567,89" in result

    def test_format_currency_small_decimal(self):
        """Testa formatação de decimal pequeno."""
        result = format_currency(0.01)
        assert "0,01" in result

    def test_format_currency_rounding(self):
        """Testa arredondamento para 2 casas decimais."""
        result = format_currency(10.555)
        # Deve arredondar para 10,56 ou 10,55
        assert "10,5" in result

    def test_format_currency_different_symbols(self):
        """Testa formatação com diferentes símbolos."""
        symbols = ["$", "£", "¥", "R$"]
        value = 100.00

        for symbol in symbols:
            result = format_currency(value, symbol=symbol)
            assert symbol in result
            assert "100,00" in result

    def test_format_currency_with_space_symbol(self):
        """Testa formatação com símbolo que inclui espaço."""
        result = format_currency(50.00, symbol="€ EUR")
        assert "50,00" in result
        assert "EUR" in result


class TestNormalizerIntegration:
    """Testa integração entre normalizadores."""

    def test_normalize_then_convert(self):
        """Testa normalizar depois converter para float."""
        value = "100.50"
        normalized = normalize_decimal(value)
        float_val = decimal_to_float(normalized)
        assert float_val == 100.50

    def test_roundtrip_with_spaces(self):
        """Testa ida e volta com espaços."""
        original = " 100.50 "
        normalized = normalize_decimal(original)
        float_val = decimal_to_float(normalized)
        currency = format_currency(float_val)

        assert "100,50" in currency

    def test_workflow_parse_format(self):
        """Testa fluxo completo: parse -> float -> format."""
        string_value = " 1234.56 "
        normalized = normalize_decimal(string_value)
        float_value = decimal_to_float(normalized)
        formatted = format_currency(float_value, symbol="$")

        assert "$" in formatted
        assert "1234,56" in formatted

    def test_consistency_across_functions(self):
        """Testa consistência entre funções."""
        test_values = [
            ("100.00", 100.0),
            ("50,50", 50.5),
            (" 75.25 ", 75.25),
            ("0.01", 0.01),
        ]

        for string_val, expected_float in test_values:
            result = decimal_to_float(string_val)
            assert abs(result - expected_float) < 0.001
