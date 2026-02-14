"""Testes unitários para ExcelValidator."""
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.common.validators.exel_validator import ExcelValidator, validate_excel_file


class TestExcelValidator(unittest.TestCase):
    """Testes para a classe ExcelValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = ExcelValidator()

    def test_validator_initialization(self) -> None:
        """Testa a inicialização do validador com parâmetros padrão."""
        self.assertIsInstance(self.validator, ExcelValidator)
        self.assertEqual(self.validator.max_file_size_mb, 50.0)
        self.assertEqual(self.validator.max_rows, 100000)
        self.assertFalse(self.validator.allow_macros)
        self.assertFalse(self.validator.allow_external_links)

    def test_custom_validator_initialization(self) -> None:
        """Testa a inicialização com parâmetros customizados."""
        validator = ExcelValidator(
            max_file_size_mb=5.0,
            max_rows=50000,
            allow_macros=True,
            allow_external_links=True,
        )
        self.assertEqual(validator.max_file_size_mb, 5.0)
        self.assertEqual(validator.max_rows, 50000)
        self.assertTrue(validator.allow_macros)
        self.assertTrue(validator.allow_external_links)

    def test_file_not_found(self) -> None:
        """Testa validação de ficheiro não existente."""
        non_existent_file = Path("non_existent_file.xlsx")
        result = self.validator.validar_arquivo(non_existent_file)
        self.assertFalse(result["valido"])
        self.assertFalse(result["avisos"])
        self.assertTrue(result["erros"])

    def test_invalid_extension(self) -> None:
        """Testa validação de ficheiro com extensão inválida."""
        with NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            result = self.validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
            self.assertIn("Extensão não permitida", str(result["erros"]))
        finally:
            temp_file.unlink()

    def test_empty_file(self) -> None:
        """Testa validação de ficheiro vazio."""
        with NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            temp_file = Path(f.name)

        try:
            result = self.validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()

    def test_is_valid_method(self) -> None:
        """Testa o método is_valid com ficheiro inválido."""
        with NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            self.assertFalse(self.validator.is_valid(temp_file))
            errors = self.validator.get_errors()
            self.assertIn("excel_file", errors)
            self.assertTrue(len(errors["excel_file"]) > 0)
        finally:
            temp_file.unlink()

    def test_convenience_function(self) -> None:
        """Testa a função de conveniência validate_excel_file."""
        with NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            result = validate_excel_file(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
