"""TableViewModel - Stage 2 table logic.

Manages state and logic for wizard Stage 2 (table page).
"""

from __future__ import annotations

import logging
from decimal import Decimal
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

        Emits:
            row_added: With row index
            table_data_changed: With updated table
            totals_updated: With recalculated totals
        """
        # Add to internal list
        self._table_rows.append(row_data)
        new_index = len(self._table_rows) - 1

        # Emit signals
        self.row_added.emit(new_index)
        self.table_data_changed.emit(self.table_rows)

        # Recalculate totals
        self.on_calculate_totals()

        logger.debug(
            f"Linha adicionada: index={new_index}, dia={row_data.dia}"
        )

    @Slot(int)
    def on_remove_row(self, index: int) -> None:
        """Remove row from table.

        Args:
            index: Index of row to remove

        Emits:
            row_removed: With removed index
            table_data_changed: With updated table
            totals_updated: With recalculated totals
        """
        if index < 0 or index >= len(self._table_rows):
            logger.warning(f"Índice inválido para remoção: {index}")
            return

        # Remove from list
        removed_row = self._table_rows.pop(index)

        # Emit signals
        self.row_removed.emit(index)
        self.table_data_changed.emit(self.table_rows)

        # Recalculate totals
        self.on_calculate_totals()

        logger.debug(f"Linha removida: index={index}, dia={removed_row.dia}")

    @Slot(int, object)
    def on_update_row(
        self, index: int, row_data: TableRowData
    ) -> None:
        """Update existing row.

        Args:
            index: Index of row to update
            row_data: New TableRowData

        Emits:
            table_data_changed: With updated table
            totals_updated: With recalculated totals
        """
        if index < 0 or index >= len(self._table_rows):
            logger.warning(f"Índice inválido para atualização: {index}")
            return

        # Update row
        self._table_rows[index] = row_data

        # Emit signals
        self.table_data_changed.emit(self.table_rows)

        # Recalculate totals
        self.on_calculate_totals()

        logger.debug(
            f"Linha atualizada: index={index}, dia={row_data.dia}"
        )

    @Slot()
    def on_calculate_totals(self) -> None:
        """Calculate and emit updated totals.

        Uses CalculationService to calculate totals from current table rows.

        Emits:
            totals_updated: With dict of totals
        """
        if not self._table_rows:
            # Empty table - emit zero totals
            zero_totals = {
                "total_ips": Decimal("0"),
                "total_km": Decimal("0"),
                "total_valor": Decimal("0"),
                "recibo_min": None,
                "recibo_max": None,
            }
            self.totals_updated.emit(zero_totals)
            return

        # Calculate using service
        totals = self._calculation_service.calcular_totais_tabela(
            self._table_rows
        )

        # Emit signal
        self.totals_updated.emit(totals)

        logger.debug(
            f"Totais calculados: IPs={totals.get('total_ips')}, "
            f"Valor={totals.get('total_valor')}"
        )

    @Slot()
    def on_clear_all(self) -> None:
        """Clear all table rows.

        Emits:
            table_data_changed: With empty table
            totals_updated: With zero totals
        """
        # Clear internal state
        self._table_rows = []

        # Emit signals
        self.table_data_changed.emit([])

        # Emit zero totals
        self.on_calculate_totals()

        logger.debug("Tabela limpa")
