"""WizardView - Main wizard window UI.

Pure view component for wizard main window.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QMessageBox,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.frontend.wizard.viewmodels import WizardCoordinator
    from src.frontend.wizard.views import (
        CalendarView,
        FormView,
        TableView,
    )

logger: logging.Logger = logging.getLogger(__name__)


class WizardView(QWidget):
    """Main wizard window (PURE VIEW - no business logic).

    Responsibilities:
    - Render wizard UI components
    - Display different stages
    - Connect UI events to ViewModel commands
    - Update UI based on ViewModel signals

    No business logic, no database calls, no calculations.
    """

    def __init__(
        self,
        coordinator: WizardCoordinator,
        form_view: FormView,
        table_view: TableView,
        calendar_view: CalendarView,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize WizardView.

        Args:
            coordinator: WizardCoordinator instance
            form_view: FormView instance
            table_view: TableView instance
            calendar_view: CalendarView instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.coordinator = coordinator
        self.form_view = form_view
        self.table_view = table_view
        self.calendar_view = calendar_view
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Stacked widget for stages
        self.stage_stack = QStackedWidget()
        self.stage_stack.addWidget(self.form_view)
        self.stage_stack.addWidget(self.table_view)
        self.stage_stack.addWidget(self.calendar_view)

        layout.addWidget(self.stage_stack)
        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect View signals to ViewModel commands."""
        # Listen to coordinator state changes
        self.coordinator.stage_changed.connect(
            self._on_stage_changed
        )
        self.coordinator.wizard_completed.connect(
            self._on_wizard_completed
        )
        self.coordinator.wizard_cancelled.connect(
            self._on_wizard_cancelled
        )

    def _on_stage_changed(self, stage_number: int) -> None:
        """Update UI when stage changes.

        Args:
            stage_number: New stage number (1-3)
        """
        if 1 <= stage_number <= 3:
            self.stage_stack.setCurrentIndex(stage_number - 1)
            logger.info(f"Switched to stage {stage_number}")

    def _on_wizard_completed(self) -> None:
        """Handle wizard completion."""
        logger.info("Wizard completed")

        # Show success message
        reply = QMessageBox.information(
            self,
            "Sucesso",
            "Wizard concluído com sucesso!\n\nOs dados foram salvos.",
            QMessageBox.StandardButton.Ok,
        )

        # Close window
        self.close()

    def _on_wizard_cancelled(self) -> None:
        """Handle wizard cancellation."""
        logger.info("Wizard cancelled")

        # Ask for confirmation
        reply = QMessageBox.question(
            self,
            "Confirmar Cancelamento",
            "Tem certeza que deseja cancelar?\nOs dados não salvos serão perdidos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Close window
            self.close()
        else:
            # User cancelled the cancellation - do nothing
            logger.info("Cancelamento de wizard foi cancelado")
