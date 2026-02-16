"""WizardState enum for wizard stage management.

This module defines the wizard navigation states and stages.
"""

from __future__ import annotations

from enum import Enum, auto


class WizardState(str, Enum):
    """Wizard navigation states.

    Defines the different stages/pages of the wizard flow.
    """

    STAGE_1_FORM = "stage_1_form"
    STAGE_2_TABLE = "stage_2_table"
    STAGE_3_CALENDAR = "stage_3_calendar"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        """String representation of wizard state.

        Returns:
            State name
        """
        return self.value

    @property
    def is_active(self) -> bool:
        """Check if wizard is in an active stage.

        Returns:
            True if not completed or cancelled
        """
        return self not in (
            WizardState.COMPLETED,
            WizardState.CANCELLED,
        )

    @property
    def stage_number(self) -> int | None:
        """Get numeric stage number.

        Returns:
            Stage number (1-3) or None if not a stage
        """
        stage_map = {
            WizardState.STAGE_1_FORM: 1,
            WizardState.STAGE_2_TABLE: 2,
            WizardState.STAGE_3_CALENDAR: 3,
        }
        return stage_map.get(self)

    def can_advance_to(self, next_state: WizardState) -> bool:
        """Check if can advance to next state.

        Args:
            next_state: Target state to advance to

        Returns:
            True if transition is valid
        """
        # Define valid transitions
        valid_transitions: dict[WizardState, set[WizardState]] = {
            WizardState.STAGE_1_FORM: {
                WizardState.STAGE_2_TABLE,
                WizardState.CANCELLED,
            },
            WizardState.STAGE_2_TABLE: {
                WizardState.STAGE_1_FORM,
                WizardState.STAGE_3_CALENDAR,
                WizardState.CANCELLED,
            },
            WizardState.STAGE_3_CALENDAR: {
                WizardState.STAGE_2_TABLE,
                WizardState.COMPLETED,
                WizardState.CANCELLED,
            },
            WizardState.COMPLETED: set(),
            WizardState.CANCELLED: set(),
        }

        return next_state in valid_transitions.get(self, set())


class WizardAction(Enum):
    """Actions that can be performed in wizard.

    Used for command pattern in ViewModels.
    """

    GO_NEXT = auto()
    GO_BACK = auto()
    GO_TO_STAGE = auto()
    SAVE_DRAFT = auto()
    LOAD_DRAFT = auto()
    VALIDATE_CURRENT = auto()
    EXPORT_PDF = auto()
    EXPORT_EXCEL = auto()
    CANCEL = auto()
    COMPLETE = auto()
