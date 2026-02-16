"""TableView - Stage 2 table UI component.

Pure view for wizard Stage 2 (table page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QPushButton,
    QTableWidget,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.frontend.wizard.viewmodels import TableViewModel

logger: logging.Logger = logging.getLogger(__name__)


class TableView(QWidget):
    """Stage 2 table UI (PURE VIEW - no business logic).

    Responsibilities:
    - Render receipts table
    - Connect table events to ViewModel
    - Update UI based on ViewModel signals

    No business logic, no calculations.
    """

    def __init__(
        self,
        viewmodel: TableViewModel,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize TableView.

        Args:
            viewmodel: TableViewModel instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Table widget
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(
            [
                "Dia",
                "Recibo Início",
                "Recibo Fim",
                "IPs",
                "Valor",
                "KM",
                "Locais",
            ]
        )
        layout.addWidget(self.table)

        # Buttons
        self.add_row_button = QPushButton("Adicionar Linha")
        self.remove_row_button = QPushButton("Remover Linha")
        self.next_button = QPushButton("Próximo")

        layout.addWidget(self.add_row_button)
        layout.addWidget(self.remove_row_button)
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect View signals to ViewModel commands."""
        # Table data changes ← ViewModel
        self.viewmodel.table_data_changed.connect(
            self._on_table_data_changed
        )
        self.viewmodel.row_added.connect(self._on_row_added)
        self.viewmodel.row_removed.connect(self._on_row_removed)
        self.viewmodel.totals_updated.connect(
            self._on_totals_updated
        )

    @Slot(list)
    def _on_table_data_changed(
        self, rows: list[object]
    ) -> None:
        """Update table UI with new data.

        Args:
            rows: List of TableRowData
        """
        logger.info(f"Table data changed: {len(rows)} rows")
        # TODO: Update table widget

    @Slot(int)
    def _on_row_added(self, index: int) -> None:
        """Handle row addition.

        Args:
            index: Index where row was added
        """
        logger.info(f"Row added at index {index}")
        # TODO: Insert row in table widget

    @Slot(int)
    def _on_row_removed(self, index: int) -> None:
        """Handle row removal.

        Args:
            index: Index where row was removed
        """
        logger.info(f"Row removed at index {index}")
        # TODO: Remove row from table widget

    @Slot(dict)
    def _on_totals_updated(self, totals: dict[str, object]) -> None:
        """Update totals display.

        Args:
            totals: Dictionary with calculated totals
        """
        logger.info(f"Totals updated: {totals}")
        # TODO: Update totals display
