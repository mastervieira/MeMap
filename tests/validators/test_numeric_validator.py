"""Testes unitários para NumericValidator."""
import unittest
from decimal import Decimal

from src.common.validators.numeric_validator import (
    NumericValidator,
    validate_numeric_field,
)


class TestNumericValidator(unittest.TestCase):
    """Testes para a classe NumericValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = NumericValidator()

    def test_valid_int_field(self) -> None:
        """Testa validação de campo inteiro válido."""
        result = self.validator.validate_field("age", "25", value_type="int")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, 25)
        self.assertEqual(result.value_type, "int")

    def test_valid_float_field(self) -> None:
        """Testa validação de campo float válido."""
        result = self.validator.validate_field("price", "19.99", value_type="float")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, 19.99)
        self.assertEqual(result.value_type, "float")

    def test_valid_decimal_field(self) -> None:
        """Testa validação de campo decimal válido."""
        result = self.validator.validate_field("amount", "100.50", value_type="decimal")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, Decimal("100.50"))
        self.assertEqual(result.value_type, "decimal")

    def test_valid_percentage_field(self) -> None:
        """Testa validação de campo percentual válido."""
        result = self.validator.validate_field("discount", "10%", value_type="percentage")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, 10.0)
        self.assertEqual(result.value_type, "percentage")

    def test_invalid_type(self) -> None:
        """Testa validação com tipo não suportado."""
        result = self.validator.validate_field("invalid", "value", value_type="invalid")
        self.assertFalse(result.is_valid)
        self.assertTrue(result.errors)

    def test_empty_value(self) -> None:
        """Testa validação com valor vazio."""
        result = self.validator.validate_field("empty", None)
        self.assertFalse(result.is_valid)
        self.assertTrue(result.errors)

    def test_out_of_range_value(self) -> None:
        """Testa validação com valor fora do range."""
        result = self.validator.validate_field("age", "150", value_type="int", min_value=0, max_value=120)
        self.assertFalse(result.is_valid)
        self.assertFalse(result.is_in_range)
        self.assertTrue(result.errors)

    def test_invalid_precision(self) -> None:
        """Testa validação com precisão inválida."""
        result = self.validator.validate_field("price", "19.999", value_type="float", decimal_places=2)
        self.assertFalse(result.is_valid)
        self.assertFalse(result.is_precision_valid)
        self.assertTrue(result.errors)

    def test_invalid_numeric_string(self) -> None:
        """Testa validação com string não numérica."""
        result = self.validator.validate_field("number", "abc", value_type="int")
        self.assertFalse(result.is_valid)
        self.assertTrue(result.errors)

    def test_comma_decimal_separator(self) -> None:
        """Testa validação com separador decimal virgula."""
        result = self.validator.validate_field("price", "19,99", value_type="float")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, 19.99)

    def test_validate_multiple_fields(self) -> None:
        """Testa validação de múltiplos campos."""
        fields = {
            "age": {"value": "25", "type": "int", "min": 0, "max": 120},
            "price": {"value": "19.99", "type": "float", "decimal_places": 2},
            "discount": {"value": "10%", "type": "percentage"},
        }
        results = self.validator.validate_multiple(fields)
        self.assertEqual(len(results), 3)
        self.assertTrue(results["age"].is_valid)
        self.assertTrue(results["price"].is_valid)
        self.assertTrue(results["discount"].is_valid)

    def test_is_valid_method(self) -> None:
        """Testa o método is_valid com dicionário de dados."""
        data = {"field_name": "age", "value": "25"}
        self.assertTrue(self.validator.is_valid(data))
        errors = self.validator.get_errors()
        self.assertEqual(errors, {})

    def test_get_errors_method(self) -> None:
        """Testa o método get_errors para obter erros."""
        data = {"field_name": "age", "value": "abc"}
        self.assertFalse(self.validator.is_valid(data))
        errors = self.validator.get_errors()
        self.assertIn("numeric_field", errors)
        self.assertTrue(len(errors["numeric_field"]) > 0)

    def test_convenience_function(self) -> None:
        """Testa a função de conveniência validate_numeric_field."""
        result = validate_numeric_field("age", "25", "int", 0, 120)
        self.assertTrue(result["valido"])
        self.assertEqual(result["campo"], "age")
        self.assertEqual(result["valor_convertido"], "25")

    def test_field_with_config(self) -> None:
        """Testa validação de campo com configuração prédefinida."""
        result = self.validator.validate_field("age", "25")
        self.assertTrue(result.is_valid)
        self.assertEqual(result.converted_value, 25)

    def test_large_number_validation(self) -> None:
        """Testa validação de número muito grande."""
        result = self.validator.validate_field("salary", "1000000", "int")
        self.assertTrue(result.is_valid)


if __name__ == "__main__":
    unittest.main()
