"""FormView - Stage 1 form UI component.

Pure view for wizard Stage 1 (form page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QTimer, Slot
from PySide6.QtWidgets import (
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from src.frontend.wizard.viewmodels import FormViewModel

logger: logging.Logger = logging.getLogger(__name__)


class FormView(QWidget):
    """Stage 1 form UI (PURE VIEW - no business logic).

    Responsibilities:
    - Render form fields
    - Connect field changes to ViewModel
    - Update UI based on ViewModel signals

    No business logic, no validation, no calculations.
    """

    def __init__(
        self,
        viewmodel: FormViewModel,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize FormView.

        Args:
            viewmodel: FormViewModel instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.viewmodel = viewmodel
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        # Form fields
        form_layout = QFormLayout()

        self.quantidade_input = QLineEdit()
        form_layout.addRow(
            "Quantidade Recibos:", self.quantidade_input
        )

        self.recibo_inicio_input = QLineEdit()
        form_layout.addRow(
            "Recibo Início:", self.recibo_inicio_input
        )

        # Recibo Fim com label de auto-cálculo
        recibo_fim_layout = QHBoxLayout()
        self.recibo_fim_input = QLineEdit()
        self.recibo_fim_input.setReadOnly(True)  # Auto-calculado
        recibo_fim_layout.addWidget(self.recibo_fim_input)

        # Label indicando auto-cálculo
        auto_calc_label = QLabel("(calculado automaticamente)")
        auto_calc_label.setStyleSheet(
            "QLabel { color: gray; font-style: italic; "
            "font-size: 10px; }"
        )
        recibo_fim_layout.addWidget(auto_calc_label)
        recibo_fim_layout.addStretch()

        form_layout.addRow("Recibo Fim:", recibo_fim_layout)

        self.zona_primaria_input = QLineEdit()
        form_layout.addRow(
            "Zona Primária:", self.zona_primaria_input
        )

        self.zona_secundaria_input = QLineEdit()
        form_layout.addRow(
            "Zona Secundária:", self.zona_secundaria_input
        )

        self.total_km_input = QLineEdit()
        form_layout.addRow("Total KM:", self.total_km_input)

        layout.addLayout(form_layout)

        # NEW: Error label para validação de range de recibos
        self.error_label = QLabel("")
        self.error_label.setWordWrap(True)
        self.error_label.setVisible(False)
        self.error_label.setStyleSheet(
            "QLabel { "
            "color: #721c24; "
            "padding: 10px; "
            "background-color: #f8d7da; "
            "border: 1px solid #f5c6cb; "
            "border-radius: 5px; "
            "font-weight: bold; "
            "}"
        )
        layout.addWidget(self.error_label)

        # Buttons
        self.next_button = QPushButton("Próximo")
        layout.addWidget(self.next_button)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect View signals to ViewModel commands."""
        # Field changes → ViewModel
        self.quantidade_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed(
                "quantidade_recibos", text
            )
        )
        self.recibo_inicio_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed(
                "recibo_inicio", text
            )
        )
        self.recibo_fim_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed(
                "recibo_fim", text
            )
        )
        self.zona_primaria_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed(
                "zona_primaria", text
            )
        )
        self.zona_secundaria_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed(
                "zona_secundaria", text
            )
        )
        self.total_km_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed(
                "total_km", text
            )
        )

        # NEW: Auto-calculation ← ViewModel
        self.viewmodel.recibo_fim_auto_calculated.connect(
            self._on_recibo_fim_calculated
        )

        # Validation results ← ViewModel
        self.viewmodel.validation_error.connect(
            self._on_validation_error
        )
        self.viewmodel.validation_success.connect(
            self._on_validation_success
        )
        # NEW: Validation cleared ← ViewModel
        self.viewmodel.validation_cleared.connect(
            self._on_validation_cleared
        )

        # Navigation buttons → Coordinator
        # Note: Coordinator is not directly accessible here
        # Will be connected at application level during initialization

    @Slot(int)
    def _on_recibo_fim_calculated(self, recibo_fim: int) -> None:
        """Update recibo_fim field when auto-calculated.

        Args:
            recibo_fim: Calculated ending receipt number
        """
        # Block signals to avoid triggering on_field_changed
        self.recibo_fim_input.blockSignals(True)
        self.recibo_fim_input.setText(str(recibo_fim))
        self.recibo_fim_input.blockSignals(False)

        # Visual feedback: highlight green briefly
        self._highlight_field(self.recibo_fim_input, "calculated")

        logger.debug(f"✓ UI atualizada: recibo_fim = {recibo_fim}")

    @Slot(str, str)
    def _on_validation_error(
        self, field: str, message: str
    ) -> None:
        """Show validation error in UI.

        Args:
            field: Field name with error
            message: Error message
        """
        logger.warning(f"⚠️ Erro de validação em {field}: {message}")

        if field == "recibo_range":
            # Show error in dedicated error label
            self.error_label.setText(message)
            self.error_label.setVisible(True)

            # Visual feedback: red border on recibo fields
            self.recibo_inicio_input.setStyleSheet(
                "QLineEdit { border: 2px solid #dc3545; "
                "background-color: #fff5f5; }"
            )
            self.recibo_fim_input.setStyleSheet(
                "QLineEdit { border: 2px solid #dc3545; "
                "background-color: #fff5f5; }"
            )

    @Slot(str)
    def _on_validation_cleared(self, field: str) -> None:
        """Clear validation error.

        Args:
            field: Field name to clear
        """
        logger.debug(f"✓ Validação limpa: {field}")

        if field == "recibo_range":
            # Hide error label
            self.error_label.setVisible(False)

            # Remove red styling
            self.recibo_inicio_input.setStyleSheet("")
            self.recibo_fim_input.setStyleSheet("")

    @Slot()
    def _on_validation_success(self) -> None:
        """Handle successful validation."""
        logger.info("✓ Validação do formulário bem-sucedida")

        # Enable next button
        self.next_button.setEnabled(True)

        # Clear error label
        self.error_label.setVisible(False)

        # Visual feedback: green border briefly
        self._highlight_field(self.next_button, "success")

    def _highlight_field(
        self, widget: QWidget, highlight_type: str
    ) -> None:
        """Temporarily highlight field with visual feedback.

        Args:
            widget: Widget to highlight
            highlight_type: Type of highlight ('calculated', 'error')
        """
        if highlight_type == "calculated":
            # Green highlight for auto-calculated values
            widget.setStyleSheet(
                "QLineEdit { "
                "background-color: #d4edda; "
                "border: 2px solid #28a745; "
                "}"
            )

            # Remove highlight after 1.5 seconds
            QTimer.singleShot(
                1500,
                lambda: widget.setStyleSheet("")
                if not widget.isReadOnly()
                else None,
            )
