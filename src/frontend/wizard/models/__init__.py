"""Data models for wizard stages.

This module contains dataclasses and enums for managing wizard state:
- FormData: Stage 1 form data structure
- TableRowData: Stage 2 table row structure
- WizardState: Enum for wizard navigation states
- WizardAction: Enum for wizard actions/commands
"""

from .form_data import FormData
from .table_data import TableRowData
from .wizard_state import WizardAction, WizardState

__all__ = ["FormData", "TableRowData", "WizardState", "WizardAction"]
