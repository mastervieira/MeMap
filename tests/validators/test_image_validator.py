"""Testes unitários para ImageValidator."""
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.common.validators.image_validator import ImageValidator, validate_image_file


class TestImageValidator(unittest.TestCase):
    """Testes para a classe ImageValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = ImageValidator()

    def test_validator_initialization(self) -> None:
        """Testa a inicialização do validador com parâmetros padrão."""
        self.assertIsInstance(self.validator, ImageValidator)
        self.assertEqual(self.validator.max_file_size_mb, 50.0)
        self.assertEqual(self.validator.max_width, 8192)
        self.assertEqual(self.validator.max_height, 8192)
        self.assertTrue(self.validator.sanitize)
        self.assertTrue(self.validator.cache_enabled)

    def test_custom_validator_initialization(self) -> None:
        """Testa a inicialização com parâmetros customizados."""
        validator = ImageValidator(
            max_file_size_mb=2.0,
            max_width=2000,
            max_height=1500,
            sanitize=False,
            cache_enabled=False,
        )
        self.assertEqual(validator.max_file_size_mb, 2.0)
        self.assertEqual(validator.max_width, 2000)
        self.assertEqual(validator.max_height, 1500)
        self.assertFalse(validator.sanitize)
        self.assertFalse(validator.cache_enabled)

    def test_file_not_found(self) -> None:
        """Testa validação de ficheiro não existente."""
        non_existent_file = Path("non_existent_image.jpg")
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
        with NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_file = Path(f.name)

        try:
            result = self.validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()

    def test_invalid_image_data(self) -> None:
        """Testa validação de ficheiro com dados inválidos."""
        with NamedTemporaryFile(suffix=".jpg", delete=False, mode="w") as f:
            f.write("invalid image data")
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
            self.assertIn("image_file", errors)
            self.assertTrue(len(errors["image_file"]) > 0)
        finally:
            temp_file.unlink()

    def test_convenience_function(self) -> None:
        """Testa a função de conveniência validate_image_file."""
        with NamedTemporaryFile(suffix=".txt", delete=False, mode="w") as f:
            f.write("test content")
            temp_file = Path(f.name)

        try:
            result = validate_image_file(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
