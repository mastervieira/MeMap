"""WizardCoordinator - Main coordinator for wizard stages.

Orchestrates navigation and state management across all stages.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal, Slot

from src.frontend.wizard.models import WizardState

if TYPE_CHECKING:
    from src.frontend.wizard.viewmodels import (
        CalendarViewModel,
        FormViewModel,
        TableViewModel,
    )

logger: logging.Logger = logging.getLogger(__name__)


class WizardCoordinator(QObject):
    """Coordinates wizard stages and global state.

    Responsibilities:
    - Manage transitions between stages
    - Maintain global wizard state
    - Orchestrate services
    - Coordinate ViewModels

    Signals:
        state_changed: Emitted when wizard state changes
        stage_changed: Emitted when stage changes (stage_number)
        wizard_completed: Emitted when wizard is completed
        wizard_cancelled: Emitted when wizard is cancelled
        error_occurred: Emitted on error (message)
    """

    # Signals
    state_changed = Signal(object)  # WizardState
    stage_changed = Signal(int)  # stage_number
    wizard_completed = Signal()
    wizard_cancelled = Signal()
    error_occurred = Signal(str)  # error_message

    def __init__(
        self,
        form_viewmodel: FormViewModel,
        table_viewmodel: TableViewModel,
        calendar_viewmodel: CalendarViewModel,
        parent: QObject | None = None,
    ) -> None:
        """Initialize WizardCoordinator.

        Args:
            form_viewmodel: FormViewModel instance
            table_viewmodel: TableViewModel instance
            calendar_viewmodel: CalendarViewModel instance
            parent: Parent QObject
        """
        super().__init__(parent)
        self._form_vm: FormViewModel = form_viewmodel
        self._table_vm: TableViewModel = table_viewmodel
        self._calendar_vm: CalendarViewModel = calendar_viewmodel
        self._current_state: WizardState = WizardState.STAGE_1_FORM

    @property
    def current_state(self) -> WizardState:
        """Get current wizard state.

        Returns:
            Current WizardState
        """
        return self._current_state

    @property
    def current_stage(self) -> int | None:
        """Get current stage number.

        Returns:
            Current stage number (1-3) or None
        """
        return self._current_state.stage_number

    @Slot()
    def on_next_stage(self) -> None:
        """Advance to next stage.

        Validates current stage before advancing.

        Emits:
            stage_changed: With new stage number
            state_changed: With new WizardState
            error_occurred: If validation fails or at last stage
        """
        current_stage = self._current_state.stage_number

        # Check if already at last stage
        if current_stage >= 3:
            self.error_occurred.emit("Já está na última etapa")
            return

        # Validate current stage before advancing
        if not self._validate_current_stage():
            self.error_occurred.emit(
                f"Etapa {current_stage} inválida. Corrija os erros antes de avançar."
            )
            return

        # Determine next state
        next_state_map = {
            WizardState.STAGE_1_FORM: WizardState.STAGE_2_TABLE,
            WizardState.STAGE_2_TABLE: WizardState.STAGE_3_CALENDAR,
        }

        next_state = next_state_map.get(self._current_state)
        if not next_state:
            self.error_occurred.emit("Transição de estado inválida")
            return

        # Update state
        self._current_state = next_state
        new_stage = self._current_state.stage_number

        # Emit signals
        self.stage_changed.emit(new_stage)
        self.state_changed.emit(self._current_state)

        logger.info(f"Avançado para etapa {new_stage}")

    @Slot()
    def on_previous_stage(self) -> None:
        """Go back to previous stage.

        Emits:
            stage_changed: With new stage number
            state_changed: With new WizardState
            error_occurred: If at first stage
        """
        current_stage = self._current_state.stage_number

        # Check if already at first stage
        if current_stage <= 1:
            self.error_occurred.emit("Já está na primeira etapa")
            return

        # Determine previous state
        prev_state_map = {
            WizardState.STAGE_2_TABLE: WizardState.STAGE_1_FORM,
            WizardState.STAGE_3_CALENDAR: WizardState.STAGE_2_TABLE,
        }

        prev_state = prev_state_map.get(self._current_state)
        if not prev_state:
            self.error_occurred.emit("Transição de estado inválida")
            return

        # Update state
        self._current_state = prev_state
        new_stage = self._current_state.stage_number

        # Emit signals
        self.stage_changed.emit(new_stage)
        self.state_changed.emit(self._current_state)

        logger.info(f"Voltado para etapa {new_stage}")

    @Slot(int)
    def on_go_to_stage(self, stage_number: int) -> None:
        """Go to specific stage.

        Args:
            stage_number: Target stage (1-3)

        Emits:
            stage_changed: With new stage number
            state_changed: With new WizardState
            error_occurred: If invalid stage or transition not allowed
        """
        # Validate stage number
        if stage_number < 1 or stage_number > 3:
            self.error_occurred.emit(
                f"Etapa inválida: {stage_number} (deve ser 1-3)"
            )
            return

        # Map stage number to state
        stage_map = {
            1: WizardState.STAGE_1_FORM,
            2: WizardState.STAGE_2_TABLE,
            3: WizardState.STAGE_3_CALENDAR,
        }

        target_state: WizardState = stage_map[stage_number]

        # Check if transition is allowed using WizardState.can_advance_to()
        if not self._current_state.can_advance_to(target_state):
            self.error_occurred.emit(
                f"Não é possível avançar de {self._current_state.stage_number} "
                f"para {stage_number}"
            )
            return

        # Update state
        self._current_state = target_state

        # Emit signals
        self.stage_changed.emit(stage_number)
        self.state_changed.emit(self._current_state)

        logger.info(f"Navegado para etapa {stage_number}")

    @Slot()
    def on_complete_wizard(self) -> None:
        """Complete wizard and save all data.

        Validates all stages and performs final save.

        Emits:
            wizard_completed: On success
            error_occurred: On validation failure or save error
        """
        # Must be at final stage
        if self._current_state != WizardState.STAGE_3_CALENDAR:
            self.error_occurred.emit(
                "Deve estar na etapa 3 para completar o wizard"
            )
            return

        # Validate all stages
        # (This logic will be refined when integrating with complete save)
        logger.info("Validando todas as etapas...")

        # TODO: Implement complete validation of all stages
        # TODO: Call DataService for final save

        # Update state
        self._current_state = WizardState.COMPLETED

        # Emit signal
        self.wizard_completed.emit()
        self.state_changed.emit(self._current_state)

        logger.info("✓ Wizard completado com sucesso")

    @Slot()
    def on_cancel_wizard(self) -> None:
        """Cancel wizard and discard changes.

        Emits:
            wizard_cancelled: Always
            state_changed: With CANCELLED state
        """
        # Update state
        self._current_state = WizardState.CANCELLED

        # Emit signals
        self.wizard_cancelled.emit()
        self.state_changed.emit(self._current_state)

        logger.info("Wizard cancelado")

    @Slot()
    def on_save_draft(self) -> None:
        """Save current state as draft.

        NOTA: Implementação simplificada para Phase 3.
        Lógica completa será refinada na integração com Views.

        Emits:
            error_occurred: On save error
        """
        logger.info("Salvando rascunho...")

        # TODO Phase 3: Implement complete orchestration of save
        # 1. Collect data from FormViewModel
        # 2. Collect data from TableViewModel
        # 3. Use DataService to save wizard_data
        # 4. Mark day as saved in CalendarViewModel

        # Placeholder
        self.error_occurred.emit(
            "Save draft será implementado na integração com Views"
        )

    @Slot(int, int)
    def on_load_draft(self, mes: int, ano: int) -> None:
        """Load draft for month/year.

        NOTA: Implementação simplificada para Phase 3.
        Lógica completa será refinada na integração com Views.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Emits:
            error_occurred: On load error
        """
        logger.info(f"Carregando rascunho para {mes}/{ano}...")

        # TODO Phase 3: Implement complete orchestration of load
        # 1. Use DataService to load wizard_data
        # 2. Distribute data to FormViewModel
        # 3. Distribute data to TableViewModel
        # 4. Update CalendarViewModel with saved days

        # Placeholder
        self.error_occurred.emit(
            "Load draft será implementado na integração com Views"
        )

    def _validate_current_stage(self) -> bool:
        """Validate current stage before allowing transition.

        Returns:
            True if current stage is valid
        """
        if self._current_state == WizardState.STAGE_1_FORM:
            # Validate form using FormViewModel
            # Esta validação será sincronizada com FormViewModel.on_validate()
            # Por agora, assumir válido (refinado na integração)
            return True

        elif self._current_state == WizardState.STAGE_2_TABLE:
            # Validate table has at least one row
            if len(self._table_vm.table_rows) == 0:
                logger.warning("Tabela vazia na validação")
                return False
            return True

        elif self._current_state == WizardState.STAGE_3_CALENDAR:
            # Stage 3 always valid (final review)
            return True

        return False
