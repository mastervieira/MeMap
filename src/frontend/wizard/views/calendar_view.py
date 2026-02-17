"""CalendarView - Stage 3 calendar UI component.

Pure view for wizard Stage 3 (calendar page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Slot
from PySide6.QtGui import QColor, QTextCharFormat
from PySide6.QtWidgets import (
    QCalendarWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.frontend.wizard.viewmodels import CalendarViewModel
logger: logging.Logger = logging.getLogger(__name__)


class CalendarView(QWidget):
    """Stage 3 calendar UI (PURE VIEW - no business logic).

    Responsibilities:
    - Render monthly calendar
    - Connect calendar events to ViewModel
    - Update UI based on ViewModel signals

    No business logic, no validation.
    """

    def __init__(
        self,
        viewmodel: CalendarViewModel,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize CalendarView.

        Args:
            viewmodel: CalendarViewModel instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Calendar widget
        self.calendar = QCalendarWidget()
        layout.addWidget(self.calendar)

        # Buttons
        self.export_pdf_button = QPushButton("Exportar PDF")
        self.export_excel_button = QPushButton("Exportar Excel")
        self.complete_button = QPushButton("Concluir")

        layout.addWidget(self.export_pdf_button)
        layout.addWidget(self.export_excel_button)
        layout.addWidget(self.complete_button)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect View signals to ViewModel commands."""
        # Calendar events → ViewModel
        self.calendar.selectionChanged.connect(
            self._on_date_selection_changed
        )

        # Export/completion buttons → ViewModel
        self.export_pdf_button.clicked.connect(
            lambda: self.viewmodel.on_export_pdf("default")
        )
        self.export_excel_button.clicked.connect(
            self.viewmodel.on_export_excel
        )

        # ViewModel signals → View updates
        self.viewmodel.date_selected.connect(
            self._on_date_selected
        )
        self.viewmodel.day_marked.connect(self._on_day_marked)
        self.viewmodel.export_completed.connect(
            self._on_export_completed
        )
        self.viewmodel.export_error.connect(
            self._on_export_error
        )

    def _on_date_selection_changed(self) -> None:
        """Handle calendar date selection change."""
        selected_date = self.calendar.selectedDate()
        self.viewmodel.on_date_selected(selected_date)

    @Slot(QDate)
    def _on_date_selected(self, date: QDate) -> None:
        """Update UI when date is selected.

        Args:
            date: Selected date
        """
        logger.info(f"Date selected: {date.toString('dd/MM/yyyy')}")

        # Just update internal state (calendar is already updated)
        # Could add a status label or details panel here if needed
        logger.debug(f"UI state updated for {date.day()}/{date.month()}/{date.year()}")

    @Slot(QDate, str)
    def _on_day_marked(self, date: QDate, tipo: str) -> None:
        """Update calendar when day is marked.

        Args:
            date: Marked date
            tipo: Day type
        """
        logger.info(f"Day marked: {date.toString()} as {tipo}")

        # Create text format for cell appearance
        cell_format = QTextCharFormat()
        cell_format.setFontWeight(600)  # Bold

        # Color code by type
        if tipo.lower() == "trabalho":
            cell_format.setBackground(QColor(144, 238, 144))  # Light green
        elif tipo.lower() in ("ferias", "férias"):
            cell_format.setBackground(QColor(255, 255, 153))  # Light yellow
        elif tipo.lower() == "feriado":
            cell_format.setBackground(QColor(255, 192, 203))  # Light pink
        elif tipo.lower() in ("falta", "ausencia", "ausência"):
            cell_format.setBackground(QColor(255, 160, 122))  # Light coral

        # Apply format to date in calendar
        self.calendar.setDateTextFormat(date, cell_format)
        logger.debug(f"Calendar cell formatted for {date.toString()} as {tipo}")

    @Slot(str)
    def _on_export_completed(self, file_path: str) -> None:
        """Handle successful export.

        Args:
            file_path: Path to exported file
        """
        logger.info(f"Export completed: {file_path}")

        QMessageBox.information(
            self,
            "Exportação Concluída",
            f"Ficheiro exportado com sucesso:\n{file_path}",
        )

    @Slot(str)
    def _on_export_error(self, message: str) -> None:
        """Handle export error.

        Args:
            message: Error message
        """
        logger.error(f"Export error: {message}")

        QMessageBox.critical(
            self,
            "Erro na Exportação",
            f"Erro ao exportar:\n{message}",
        )
