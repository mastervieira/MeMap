"""ExportService - Export data to PDF/Excel.

Handles all export functionality.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from PySide6.QtGui import QPixmap

    from src.db.models.mapas import TabelaTaxas

logger: logging.Logger = logging.getLogger(__name__)


class ExportService:
    """Manages data export to different formats.

    Responsibilities:
    - Export to PDF
    - Export to Excel
    - Generate previews
    - Validate export data
    """

    def exportar_pdf(
        self, tabela: TabelaTaxas, template: str
    ) -> Path:
        """Export mapa to PDF.

        Args:
            tabela: TabelaTaxas instance to export
            template: Template name to use

        Returns:
            Path to generated PDF file
        """
        raise NotImplementedError("To be implemented in Phase 2")

    def exportar_excel(self, tabela: TabelaTaxas) -> Path:
        """Export mapa to Excel.

        Args:
            tabela: TabelaTaxas instance to export

        Returns:
            Path to generated Excel file
        """
        raise NotImplementedError("To be implemented in Phase 2")

    def gerar_preview(
        self, tabela: TabelaTaxas
    ) -> QPixmap:
        """Generate preview image of mapa.

        Args:
            tabela: TabelaTaxas instance to preview

        Returns:
            QPixmap with preview image
        """
        raise NotImplementedError("To be implemented in Phase 2")

    def validar_exportacao(
        self, tabela: TabelaTaxas
    ) -> tuple[bool, str | None]:
        """Validate data before export.

        Args:
            tabela: TabelaTaxas instance to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        raise NotImplementedError("To be implemented in Phase 2")
