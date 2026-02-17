"""TableView - Stage 2 table UI component.

Pure view for wizard Stage 2 (table page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.frontend.wizard.models import TableRowData
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
        self.viewmodel: TableViewModel = viewmodel
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
        # Set column widths
        header: QHeaderView = self.table.horizontalHeader()
        header.setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        layout.addWidget(self.table)

        # Totals label
        self.totals_label = QLabel("")
        self.totals_label.setVisible(False)
        self.totals_label.setStyleSheet(
            "QLabel { "
            "font-weight: bold; "
            "padding: 10px; "
            "background-color: #f0f0f0; "
            "border: 1px solid #ccc; "
            "border-radius: 3px; "
            "}"
        )
        layout.addWidget(self.totals_label)

        # Buttons
        self.add_row_button = QPushButton("Adicionar Linha")
        self.remove_row_button = QPushButton("Remover Linha")
        self.next_button = QPushButton("Próximo")
        self.previous_button = QPushButton("Anterior")

        layout.addWidget(self.add_row_button)
        layout.addWidget(self.remove_row_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.previous_button)

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
        self, rows: list[TableRowData]
    ) -> None:
        """Update table UI with new data.

        Args:
            rows: List of TableRowData
        """
        logger.info(f"Table data changed: {len(rows)} rows")

        # Clear existing rows
        self.table.setRowCount(0)

        if not rows:
            self.table.setRowCount(0)
            return

        # Add rows to table
        for row_data in rows:
            row_count: int = self.table.rowCount()
            self.table.insertRow(row_count)

            # Extract data from TableRowData
            dia = str(row_data.dia)
            recibo_inicio: str = (
                str(row_data.recibo_inicio)
                if row_data.recibo_inicio is not None
                else ""
            )
            recibo_fim: str = (
                str(row_data.recibo_fim)
                if row_data.recibo_fim is not None
                else ""
            )
            ips = str(row_data.ips)
            valor: str = f"{row_data.valor_com_iva:.2f}"
            km: str = f"{row_data.km:.2f}"
            locais: str = row_data.locais

            # Create table items
            items: list[QTableWidgetItem] = [
                QTableWidgetItem(dia),
                QTableWidgetItem(recibo_inicio),
                QTableWidgetItem(recibo_fim),
                QTableWidgetItem(ips),
                QTableWidgetItem(valor),
                QTableWidgetItem(km),
                QTableWidgetItem(locais),
            ]

            # Add items to row
            for col, item in enumerate(items):
                item.setFlags(item.flags() & ~(item.flags()))
                self.table.setItem(row_count, col, item)

            logger.debug(
                f"Row {row_count}: dia={dia}, "
                f"recibo={recibo_inicio}-{recibo_fim}"
            )

    @Slot(int)
    def _on_row_added(self, index: int) -> None:
        """Handle row addition.

        Args:
            index: Index where row was added
        """
        logger.info(f"Row added at index {index}")

        # Refresh table with updated data from viewmodel
        self._on_table_data_changed(self.viewmodel.table_rows)

    @Slot(int)
    def _on_row_removed(self, index: int) -> None:
        """Handle row removal.

        Args:
            index: Index where row was removed
        """
        logger.info(f"Row removed at index {index}")

        # Refresh table with updated data from viewmodel
        self._on_table_data_changed(self.viewmodel.table_rows)

    @Slot(dict)
    def _on_totals_updated(self, totals: dict[str, object]) -> None:
        """Update totals display.

        Args:
            totals: Dictionary with calculated totals
        """
        logger.info(f"Totals updated: {totals}")

        if not totals:
            self.totals_label.setVisible(False)
            return

        # Format totals for display
        total_ips = totals.get("total_ips", 0)
        total_km = totals.get("total_km", 0)
        total_valor = totals.get("total_valor", 0)
        recibo_min = totals.get("recibo_min")
        recibo_max = totals.get("recibo_max")

        # Build display text
        text_parts = [
            f"Totais: IPs={total_ips} | "
            f"Valor=€{total_valor:.2f} | "
            f"KM={total_km:.2f}"
        ]

        if recibo_min is not None and recibo_max is not None:
            text_parts.append(
                f" | Recibos: {recibo_min}-{recibo_max}"
            )

        self.totals_label.setText("".join(text_parts))
        self.totals_label.setVisible(True)
