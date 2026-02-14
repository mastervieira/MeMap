"""Testes unitários para PdfValidator."""
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.common.validators.pdf_validator import PdfValidator, validate_pdf_file


class TestPdfValidator(unittest.TestCase):
    """Testes para a classe PdfValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = PdfValidator()

    def test_validator_initialization(self) -> None:
        """Testa a inicialização do validador com parâmetros padrão."""
        self.assertIsInstance(self.validator, PdfValidator)
        self.assertEqual(self.validator.max_file_size_mb, 100.0)
        self.assertEqual(self.validator.max_pages, 5000)
        self.assertFalse(self.validator.allow_javascript)
        self.assertFalse(self.validator.allow_embedded_files)

    def test_custom_validator_initialization(self) -> None:
        """Testa a inicialização com parâmetros customizados."""
        validator = PdfValidator(
            max_file_size_mb=5.0,
            max_pages=50,
            allow_javascript=True,
            allow_embedded_files=True,
        )
        self.assertEqual(validator.max_file_size_mb, 5.0)
        self.assertEqual(validator.max_pages, 50)
        self.assertTrue(validator.allow_javascript)
        self.assertTrue(validator.allow_embedded_files)

    def test_file_not_found(self) -> None:
        """Testa validação de ficheiro não existente."""
        non_existent_file = Path("non_existent_file.pdf")
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
        with NamedTemporaryFile(suffix=".pdf", delete=False) as f:
            temp_file = Path(f.name)

        try:
            result = self.validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()

    def test_invalid_pdf_data(self) -> None:
        """Testa validação de ficheiro com dados inválidos."""
        with NamedTemporaryFile(suffix=".pdf", delete=False, mode="w") as f:
            f.write("invalid pdf data")
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
            self.assertIn("pdf_file", errors)
            self.assertTrue(len(errors["pdf_file"]) > 0)
        finally:
            temp_file.unlink()

    def test_convenience_function(self) -> None:
        """Testa a função de conveniência validate_pdf_file."""
        with NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            result = validate_pdf_file(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
