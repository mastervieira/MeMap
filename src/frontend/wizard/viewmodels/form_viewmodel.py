"""FormViewModel - Stage 1 form logic.

Manages state and logic for wizard Stage 1 (form page).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal, Slot

if TYPE_CHECKING:
    from src.frontend.wizard.models import FormData
    from src.frontend.wizard.services import (
        DataService,
        ValidationService,
    )

logger: logging.Logger = logging.getLogger(__name__)


class FormViewModel(QObject):
    """Manages Stage 1 form state and logic.

    Responsibilities:
    - Manage form field state
    - Validate form data
    - Auto-calculate recibo_fim from quantidade + recibo_inicio
    - Validate receipt range immediately
    - Communicate with DataService for load/save
    - Emit signals for UI updates

    Signals:
        form_data_changed: Emitted when form data changes
        validation_error: Emitted on validation error (field, message)
        validation_success: Emitted on successful validation
        loading_changed: Emitted when loading state changes
        recibo_fim_auto_calculated: Emitted when recibo_fim is auto-calculated
        validation_cleared: Emitted when validation error is cleared
    """

    # Signals
    form_data_changed = Signal(object)  # FormData
    validation_error = Signal(str, str)  # field_name, message
    validation_success = Signal()
    loading_changed = Signal(bool)

    # NEW: Auto-calculation and validation signals
    recibo_fim_auto_calculated = Signal(int)  # recibo_fim value
    validation_cleared = Signal(str)  # field_name

    def __init__(
        self,
        data_service: DataService,
        validation_service: ValidationService,
        parent: QObject | None = None,
    ) -> None:
        """Initialize FormViewModel.

        Args:
            data_service: DataService instance
            validation_service: ValidationService instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self._data_service: DataService = data_service
        self._validation_service: ValidationService = validation_service
        self._form_data: FormData | None = None
        self._is_loading = False

        # NEW: Internal state for auto-calculation
        self._raw_form_data: dict[str, object] = {}
        self._current_mes: int = 0
        self._current_ano: int = 0

    @property
    def form_data(self) -> FormData | None:
        """Get current form data.

        Returns:
            Current FormData or None
        """
        return self._form_data

    @property
    def is_loading(self) -> bool:
        """Check if currently loading.

        Returns:
            True if loading
        """
        return self._is_loading

    def set_current_date(self, mes: int, ano: int) -> None:
        """Set current month/year for validation.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)
        """
        self._current_mes = mes
        self._current_ano = ano
        logger.debug(f"Data atual definida: {mes}/{ano}")

    @Slot(str, object)
    def on_field_changed(
        self, field_name: str, value: object
    ) -> None:
        """Handle field value change.

        Automatically calculates recibo_fim when quantidade or
        recibo_inicio changes. Validates receipt range immediately.

        Args:
            field_name: Name of changed field
            value: New value
        """
        # Update internal state
        self._raw_form_data[field_name] = value

        logger.debug(
            f"Campo alterado: {field_name} = {value}"
        )

        # AUTO-CÁLCULO: recibo_fim = recibo_inicio + quantidade - 1
        if field_name in ("quantidade_recibos", "recibo_inicio"):
            self._auto_calcular_recibo_fim()

        # VALIDAÇÃO IMEDIATA: validar range quando campos relevantes mudam
        if field_name in ("recibo_inicio", "recibo_fim"):
            self._validar_range_recibos_imediato()

        # Emit signal for UI update
        self.form_data_changed.emit(self._raw_form_data)

    def _auto_calcular_recibo_fim(self) -> None:
        """Calculate recibo_fim automatically.

        Formula: recibo_fim = recibo_inicio + quantidade - 1

        Emits:
            recibo_fim_auto_calculated: When calculation succeeds
        """
        try:
            quantidade: object | None = self._raw_form_data.get("quantidade_recibos")
            recibo_inicio: object | None = self._raw_form_data.get("recibo_inicio")

            # Convert to int safely
            if quantidade is None or recibo_inicio is None:
                return

            qtd = int(quantidade)  # type: ignore[arg-type]
            inicio = int(recibo_inicio)  # type: ignore[arg-type]

            if qtd > 0 and inicio > 0:
                # Formula: fim = início + quantidade - 1
                recibo_fim: int = inicio + qtd - 1

                # Update internal state
                self._raw_form_data["recibo_fim"] = recibo_fim

                # Emit signal for UI update
                self.recibo_fim_auto_calculated.emit(recibo_fim)

                logger.debug(
                    f"✓ Auto-calculado: recibo_fim = {recibo_fim} "
                    f"(início={inicio}, qtd={qtd})"
                )
        except (ValueError, TypeError) as e:
            logger.warning(
                f"Erro ao auto-calcular recibo_fim: {e}"
            )

    def _validar_range_recibos_imediato(self) -> None:
        """Validate receipt range immediately (form-level).

        Calls ValidationService.validar_range_recibos() and emits
        validation error/cleared signals.

        Emits:
            validation_error: If range is invalid
            validation_cleared: If range is valid
        """
        try:
            recibo_inicio: object | None = self._raw_form_data.get("recibo_inicio")
            recibo_fim: object | None = self._raw_form_data.get("recibo_fim")

            # Check if we have all required data
            if (
                recibo_inicio is None
                or recibo_fim is None
                or self._current_mes == 0
                or self._current_ano == 0
            ):
                return

            # Convert to int safely
            inicio = int(recibo_inicio)  # type: ignore[arg-type]
            fim = int(recibo_fim)  # type: ignore[arg-type]

            if inicio <= 0 or fim <= 0:
                return

            # Call ValidationService
            is_valid, errors = self._validation_service.validar_range_recibos(
                recibo_inicio=inicio,
                recibo_fim=fim,
                mes=self._current_mes,
                ano=self._current_ano,
            )

            if not is_valid:
                # Emit error signal
                error_msg: str = "\n".join(errors)
                self.validation_error.emit(
                    "recibo_range", error_msg
                )
                logger.warning(
                    f"⚠️ Range de recibos inválido: {error_msg}"
                )
            else:
                # Clear previous error
                self.validation_cleared.emit("recibo_range")
                logger.debug(
                    f"✓ Range de recibos válido: {inicio}-{fim}"
                )

        except (ValueError, TypeError) as e:
            logger.warning(f"Erro ao validar range: {e}")

    @Slot()
    def on_validate(self) -> None:
        """Validate current form data.

        Emits:
            validation_success: If validation passes
            validation_error: If validation fails (field, message)
        """
        # Check if there is data
        if not self._form_data:
            self.validation_error.emit("form", "Formulário vazio")
            return

        # Call ValidationService
        is_valid, errors = self._validation_service.validar_formulario(
            self._form_data
        )

        if is_valid:
            self.validation_success.emit()
            logger.info("✓ Formulário validado com sucesso")
        else:
            # Emit first error
            error_msg = "\n".join(errors)
            self.validation_error.emit("form", error_msg)
            logger.warning(f"⚠️ Validação falhou: {error_msg}")

    @Slot()
    def on_load_data(self) -> None:
        """Load form data from database.

        Uses DataService to load wizard_data for current month/year/day.

        Emits:
            loading_changed: During load operation
            form_data_changed: When data is loaded
            validation_error: If load fails
        """
        if self._current_mes == 0 or self._current_ano == 0:
            self.validation_error.emit(
                "date", "Data não definida. Use set_current_date() primeiro."
            )
            return

        try:
            # Set loading state
            self._is_loading = True
            self.loading_changed.emit(True)

            # Load mapa from database
            mapa = self._data_service.carregar_mapa(
                self._current_mes, self._current_ano
            )

            if not mapa:
                logger.info(
                    f"Nenhum mapa encontrado para "
                    f"{self._current_mes}/{self._current_ano}"
                )
                self._form_data = None
                self._raw_form_data = {}
                self.form_data_changed.emit({})
                return

            # Extract form data from wizard_data
            # Assuming there is a selected day (will be set by Coordinator)
            # For now, load base structure
            if isinstance(mapa.wizard_data, dict) and "dias" in mapa.wizard_data:
                # Example: load last edited day or specific day
                # This logic will be refined when integrating with WizardCoordinator
                logger.info(
                    f"Mapa carregado com {len(mapa.wizard_data['dias'])} dias"
                )

            # Update internal state
            self.form_data_changed.emit(self._raw_form_data)
            logger.info("✓ Dados carregados com sucesso")

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            self.validation_error.emit("load", f"Erro ao carregar: {str(e)}")

        finally:
            self._is_loading = False
            self.loading_changed.emit(False)

    @Slot()
    def on_clear(self) -> None:
        """Clear all form data.

        Resets internal state and emits signals.

        Emits:
            form_data_changed: With empty dict
            validation_cleared: For all fields
        """
        # Clear internal state
        self._form_data = None
        self._raw_form_data = {}

        # Emit signals
        self.form_data_changed.emit({})
        self.validation_cleared.emit("all")

        logger.debug("Formulário limpo")
