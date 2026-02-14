"""Testes estendidos para PdfValidator para aumentar a cobertura."""
import unittest
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.common.validators.pdf_validator import PdfValidator


class TestPdfValidatorExtended(unittest.TestCase):
    """Testes estendidos para PdfValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = PdfValidator()

    def test_encrypted_pdf(self) -> None:
        """Testa validação de PDF criptografado."""
        with NamedTemporaryFile(suffix=".pdf", delete=False, mode="wb") as f:
            f.write(b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R /Encrypt 3 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [] /Count 0 >>\nendobj\n3 0 obj\n<< /Filter /Standard /V 1 /R 2 /U (12345) /O (67890) >>\nendobj\nxref\n0 4\n0000000000 65535 f \n0000000009 00000 n \n0000000058 00000 n \n0000000101 00000 n \ntrailer\n<< /Size 4 /Root 1 0 R >>\nstartxref\n156\n%%EOF")

        try:
            temp_file = Path(f.name)
            result = self.validator.validar_arquivo(temp_file)
            self.assertTrue(result["valido"])  # PDF é válido, mas pode ter avisos
        finally:
            temp_file.unlink()

    def test_validator_with_custom_parameters(self) -> None:
        """Testa validador com parâmetros customizados."""
        validator = PdfValidator(
            max_file_size_mb=1,
            max_pages=50,
            allow_javascript=True,
            allow_embedded_files=True
        )
        self.assertEqual(validator.max_file_size_mb, 1)
        self.assertEqual(validator.max_pages, 50)
        self.assertTrue(validator.allow_javascript)
        self.assertTrue(validator.allow_embedded_files)


if __name__ == "__main__":
    unittest.main()
