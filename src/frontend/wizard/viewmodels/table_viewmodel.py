"""TableViewModel - Stage 2 table logic.

Manages state and logic for wizard Stage 2 (table page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal, Slot

if TYPE_CHECKING:
    from src.frontend.wizard.models import TableRowData
    from src.frontend.wizard.services import CalculationService

logger: logging.Logger = logging.getLogger(__name__)


class TableViewModel(QObject):
    """Manages Stage 2 table state and logic.

    Responsibilities:
    - Manage table rows
    - Add/remove receipts
    - Calculate totals via CalculationService
    - Emit signals for UI updates

    Signals:
        table_data_changed: Emitted when table data changes
        row_added: Emitted when row is added (index)
        row_removed: Emitted when row is removed (index)
        totals_updated: Emitted when totals are recalculated
        loading_changed: Emitted when loading state changes
    """

    # Signals
    table_data_changed = Signal(list)  # list[TableRowData]
    row_added = Signal(int)  # index
    row_removed = Signal(int)  # index
    totals_updated = Signal(dict)  # totals dict
    loading_changed = Signal(bool)

    def __init__(
        self,
        calculation_service: CalculationService,
        parent: QObject | None = None,
    ) -> None:
        """Initialize TableViewModel.

        Args:
            calculation_service: CalculationService instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self._calculation_service = calculation_service
        self._table_rows: list[TableRowData] = []
        self._is_loading = False

    @property
    def table_rows(self) -> list[TableRowData]:
        """Get current table rows.

        Returns:
            List of TableRowData
        """
        return self._table_rows.copy()

    @property
    def is_loading(self) -> bool:
        """Check if currently loading.

        Returns:
            True if loading
        """
        return self._is_loading

    @Slot(object)
    def on_add_row(self, row_data: TableRowData) -> None:
        """Add new row to table.

        Args:
            row_data: TableRowData to add
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot(int)
    def on_remove_row(self, index: int) -> None:
        """Remove row from table.

        Args:
            index: Index of row to remove
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot(int, object)
    def on_update_row(
        self, index: int, row_data: TableRowData
    ) -> None:
        """Update existing row.

        Args:
            index: Index of row to update
            row_data: New TableRowData
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_calculate_totals(self) -> None:
        """Calculate and emit updated totals."""
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_clear_all(self) -> None:
        """Clear all table rows."""
        raise NotImplementedError("To be implemented in Phase 3")
