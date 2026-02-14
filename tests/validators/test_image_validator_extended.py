"""Testes estendidos para ImageValidator para aumentar a cobertura."""
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from PIL import Image

from src.common.validators.image_validator import ImageValidator


class TestImageValidatorExtended(unittest.TestCase):
    """Testes estendidos para ImageValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = ImageValidator()

    def test_sanitization_with_caching(self) -> None:
        """Testa sanitização de imagem com caching."""
        with NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new('RGB', (100, 100), color='red')
            img.save(f, format='PNG')

        try:
            temp_file = Path(f.name)
            validator = ImageValidator(sanitize=True, cache_enabled=True)
            result = validator.validar_arquivo(temp_file)
            self.assertTrue(result["valido"])
            self.assertIsNotNone(result["caminho_sanitizado"])
        finally:
            temp_file.unlink()

    def test_large_image_dimensions(self) -> None:
        """Testa validação de imagem com dimensões excessivas."""
        with NamedTemporaryFile(suffix=".png", delete=False) as f:
            img = Image.new('RGB', (900, 900), color='blue')
            img.save(f, format='PNG')

        try:
            temp_file = Path(f.name)
            validator = ImageValidator(max_width=800, max_height=800)
            result = validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
        finally:
            temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
