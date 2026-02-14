"""Testes estendidos para NumericValidator para aumentar a cobertura."""
import unittest
from decimal import Decimal

from src.common.validators.numeric_validator import NumericValidator


class TestNumericValidatorExtended(unittest.TestCase):
    """Testes estendidos para NumericValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = NumericValidator()

    def test_range_validation_with_exception(self) -> None:
        """Testa validação de range com exceção."""
        result = self.validator.validate_field(
            "invalid_range",
            "10",
            "int",
            "invalid",
            "invalid"
        )
        self.assertFalse(result.is_valid)
        self.assertTrue(any("Erro ao validar range" in e for e in result.errors))

    def test_precision_validation_with_exception(self) -> None:
        """Testa validação de precisão com exceção."""
        # Criar um objeto que cause exceção ao ser convertido para string
        class BadValue:
            def __str__(self):
                raise Exception("Erro de conversão")

        result = self.validator.validate_field(
            "bad_value",
            BadValue(),
            "float",
            decimal_places=2
        )
        self.assertFalse(result.is_valid)

    def test_validate_with_valid_config(self) -> None:
        """Testa validação com configuração de campo pré-definida."""
        result = self.validator.validate_field("price", "19.99")
        self.assertTrue(result.is_valid)
        self.assertIsInstance(result.converted_value, float)
        self.assertEqual(result.converted_value, 19.99)

    def test_validate_without_field_name(self) -> None:
        """Testa validação sem nome de campo."""
        result = self.validator.validate_field("", "100")
        self.assertTrue(result.is_valid)

    def test_validate_with_empty_string_value(self) -> None:
        """Testa validação com string vazia."""
        result = self.validator.validate_field("test", "")
        self.assertFalse(result.is_valid)
        self.assertTrue(result.errors)

    def test_validate_with_negative_integer(self) -> None:
        """Testa validação de inteiro negativo."""
        result = self.validator.validate_field("test", "-10", "int")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, -10)

    def test_validate_with_large_float(self) -> None:
        """Testa validação de float com valor grande."""
        result = self.validator.validate_field("large", "1000000.1234", "float")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, 1000000.1234)

    def test_validate_with_multiple_validation_errors(self) -> None:
        """Testa validação com múltiplos erros."""
        result = self.validator.validate_field(
            "invalid",
            "abc",
            "int",
            min_value=0,
            max_value=10,
            decimal_places=2
        )
        self.assertFalse(result.is_valid)


if __name__ == "__main__":
    unittest.main()
