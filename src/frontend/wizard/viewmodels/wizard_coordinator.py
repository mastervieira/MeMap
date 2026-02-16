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
        self._form_vm = form_viewmodel
        self._table_vm = table_viewmodel
        self._calendar_vm = calendar_viewmodel
        self._current_state = WizardState.STAGE_1_FORM

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
        """Advance to next stage."""
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_previous_stage(self) -> None:
        """Go back to previous stage."""
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot(int)
    def on_go_to_stage(self, stage_number: int) -> None:
        """Go to specific stage.

        Args:
            stage_number: Target stage (1-3)
        """
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_complete_wizard(self) -> None:
        """Complete wizard and save all data."""
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_cancel_wizard(self) -> None:
        """Cancel wizard and discard changes."""
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot()
    def on_save_draft(self) -> None:
        """Save current state as draft."""
        raise NotImplementedError("To be implemented in Phase 3")

    @Slot(int, int)
    def on_load_draft(self, mes: int, ano: int) -> None:
        """Load draft for month/year.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)
        """
        raise NotImplementedError("To be implemented in Phase 3")
