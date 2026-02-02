"""
Docstring for common.validators.base_validator
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseValidator(ABC):
    """Base class for all validators."""
    pass

    @abstractmethod
    def is_valid(self, data: Any) -> bool:
        """Validate data.

        Args:
            data: Data to validate (can be anything)

        Returns:
            True if valid, False otherwise
        """
        pass

    @abstractmethod
    def get_errors(self) -> dict[str, str]:
        """Get validation errors.

        Returns:
            Dictionary where:
            - key = field name (e.g., 'email')
            - value = error message (e.g., 'Invalid email')
        """
        pass
