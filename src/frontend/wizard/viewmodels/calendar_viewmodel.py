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
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot(QDate, str)
    def on_mark_day(self, date: QDate, tipo: str) -> None:
        """Mark day with specific type.

        Args:
            date: Date to mark
            tipo: Type (trabalho, ferias, etc.)
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot(str)
    def on_export_pdf(self, template: str) -> None:
        """Export to PDF.

        Args:
            template: Template name to use
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_export_excel(self) -> None:
        """Export to Excel."""
        raise NotImplementedError("To be implemented in Phase 3")
