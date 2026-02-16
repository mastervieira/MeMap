"""CalendarViewModel - Stage 3 calendar logic.

Manages state and logic for wizard Stage 3 (calendar page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QObject, Signal, Slot

if TYPE_CHECKING:
    from src.frontend.wizard.services import (
        ExportService,
        ValidationService,
    )

logger: logging.Logger = logging.getLogger(__name__)


class CalendarViewModel(QObject):
    """Manages Stage 3 calendar state and logic.

    Responsibilities:
    - Manage working days/absences
    - Validate dates
    - Export via ExportService
    - Emit signals for UI updates

    Signals:
        date_selected: Emitted when date is selected
        day_marked: Emitted when day is marked (date, type)
        export_completed: Emitted when export is done (path)
        export_error: Emitted on export error (message)
        loading_changed: Emitted when loading state changes
    """

    # Signals
    date_selected = Signal(QDate)
    day_marked = Signal(QDate, str)  # date, tipo
    export_completed = Signal(str)  # file_path
    export_error = Signal(str)  # error_message
    error_occurred = Signal(str)  # general error_message
    loading_changed = Signal(bool)

    def __init__(
        self,
        validation_service: ValidationService,
        export_service: ExportService,
        parent: QObject | None = None,
    ) -> None:
        """Initialize CalendarViewModel.

        Args:
            validation_service: ValidationService instance
            export_service: ExportService instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self._validation_service = validation_service
        self._export_service = export_service
        self._selected_date: QDate | None = None
        self._is_loading = False

    @property
    def selected_date(self) -> QDate | None:
        """Get currently selected date.

        Returns:
            Selected QDate or None
        """
        return self._selected_date

    @property
    def is_loading(self) -> bool:
        """Check if currently loading.

        Returns:
            True if loading
        """
        return self._is_loading

    @Slot(QDate)
    def on_date_selected(self, date: QDate) -> None:
        """Handle date selection.

        Args:
            date: Selected date

        Emits:
            date_selected: With selected date
        """
        if not date.isValid():
            logger.warning("Data inválida selecionada")
            return

        # Update internal state
        self._selected_date = date

        # Emit signal
        self.date_selected.emit(date)

        logger.debug(
            f"Data selecionada: {date.day()}/{date.month()}/{date.year()}"
        )

    @Slot(QDate, str)
    def on_mark_day(self, date: QDate, tipo: str) -> None:
        """Mark day with specific type.

        Args:
            date: Date to mark
            tipo: Type (e.g., "trabalho", "ferias", "falta")

        Emits:
            day_marked: With date and type
            error_occurred: If validation fails
        """
        if not date.isValid():
            self.error_occurred.emit("Data inválida")
            return

        # Validate date using ValidationService
        is_valid = self._validation_service.validar_datas(
            date.month(), date.year()
        )

        if not is_valid:
            self.error_occurred.emit(
                f"Data inválida: {date.month()}/{date.year()}"
            )
            return

        # Emit signal (actual storage handled by WizardCoordinator/DataService)
        self.day_marked.emit(date, tipo)

        logger.debug(
            f"Dia marcado: {date.day()}/{date.month()}/{date.year()} "
            f"como '{tipo}'"
        )

    @Slot(str)
    def on_export_pdf(self, template: str) -> None:
        """Export to PDF.

        NOTA: Bloqueado até ExportService ser implementado (Phase 2).

        Args:
            template: Template name to use

        Emits:
            export_error: Currently always (not implemented)
        """
        error_msg = (
            "Exportação PDF não disponível. "
            "ExportService será implementado em Phase 2."
        )
        self.export_error.emit(error_msg)
        logger.warning(error_msg)

        # TODO Phase 2: Implementar quando ExportService estiver pronto
        # try:
        #     self._is_loading = True
        #     self.loading_changed.emit(True)
        #
        #     path = self._export_service.exportar_pdf(mapa, template)
        #     self.export_completed.emit(str(path))
        # except Exception as e:
        #     self.export_error.emit(str(e))
        # finally:
        #     self._is_loading = False
        #     self.loading_changed.emit(False)

    @Slot()
    def on_export_excel(self) -> None:
        """Export to Excel.

        NOTA: Bloqueado até ExportService ser implementado (Phase 2).

        Emits:
            export_error: Currently always (not implemented)
        """
        error_msg = (
            "Exportação Excel não disponível. "
            "ExportService será implementado em Phase 2."
        )
        self.export_error.emit(error_msg)
        logger.warning(error_msg)

        # TODO Phase 2: Implementar quando ExportService estiver pronto
