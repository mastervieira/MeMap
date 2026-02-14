"""Testes estendidos para ExcelValidator para aumentar a cobertura."""
import unittest
import zipfile
from pathlib import Path
from tempfile import NamedTemporaryFile

from src.common.validators.exel_validator import ExcelValidator


class TestExcelValidatorExtended(unittest.TestCase):
    """Testes estendidos para ExcelValidator."""

    def setUp(self) -> None:
        """Configuração pré-teste: cria instância do validador."""
        self.validator = ExcelValidator()

    def test_xlsx_with_macros(self) -> None:
        """Testa validação de XLSX contendo macros ocultas."""
        with NamedTemporaryFile(suffix=".xlsx", delete=False, mode="wb") as f:
            with zipfile.ZipFile(f, 'w') as zf:
                zf.writestr('[Content_Types].xml', '')
                zf.writestr('_rels/.rels', '')
                zf.writestr('xl/workbook.xml', '')
                zf.writestr('xl/_rels/workbook.xml.rels', '')
                zf.writestr('xl/vbaProject.bin', '')

        try:
            temp_file = Path(f.name)
            result = self.validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
            self.assertTrue(result["tem_macros"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()

    def test_validator_with_custom_parameters(self) -> None:
        """Testa validador com parâmetros customizados."""
        validator = ExcelValidator(
            max_file_size_mb=1,
            max_rows=1000,
            allow_macros=True,
            allow_external_links=True
        )
        self.assertEqual(validator.max_file_size_mb, 1)
        self.assertEqual(validator.max_rows, 1000)
        self.assertTrue(validator.allow_macros)
        self.assertTrue(validator.allow_external_links)

    def test_empty_file_validation(self) -> None:
        """Testa validação de arquivo vazio."""
        with NamedTemporaryFile(suffix=".xlsx", delete=False, mode="wb") as f:
            temp_file = Path(f.name)

        try:
            result = self.validator.validar_arquivo(temp_file)
            self.assertFalse(result["valido"])
            self.assertFalse(result["avisos"])
            self.assertTrue(result["erros"])
        finally:
            temp_file.unlink()


if __name__ == "__main__":
    unittest.main()
