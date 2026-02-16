"""Toast notification configuration and constants."""

from dataclasses import dataclass
from enum import Enum
from typing import Final

from PySide6.QtCore import QEasingCurve


class CloseReason(Enum):
    """Reason for toast closure."""
    AUTO = "auto"  # Timer expired
    MANUAL = "manual"  # User clicked close button
    PROGRAMMATIC = "programmatic"  # Closed by code (clear_all, limit exceeded)


class ToastType(Enum):
    """Toast notification type."""
    SUCCESS = "success"
    ERROR = "error"
    INFO = "info"
    WARNING = "warning"


@dataclass(frozen=True)
class ToastConfig:
    """Immutable configuration for toast notifications."""

    # Limits
    MAX_TOASTS: Final[int] = 5
    DEDUP_WINDOW_MS: Final[int] = 2000

    # Dimensions (pixels)
    WIDTH: Final[int] = 350
    MIN_HEIGHT: Final[int] = 64

    # Positioning (pixels)
    MARGIN: Final[int] = 20
    SPACING: Final[int] = 10

    # Animation durations (milliseconds)
    SLIDE_IN_DURATION: Final[int] = 400
    REPOSITION_DURATION: Final[int] = 300
    FADE_OUT_DURATION: Final[int] = 200
    SLIDE_OFFSET: Final[int] = 40

    # Display durations by type (milliseconds)
    DURATION_SUCCESS: Final[int] = 3000
    DURATION_ERROR: Final[int] = 5000
    DURATION_INFO: Final[int] = 3000
    DURATION_WARNING: Final[int] = 4000

    # Animation curves
    SLIDE_EASING: Final[QEasingCurve.Type] = QEasingCurve.Type.OutCubic
    REPOSITION_EASING: Final[QEasingCurve.Type] = QEasingCurve.Type.OutCubic

    def get_duration_for_type(self, toast_type: ToastType) -> int:
        """Get display duration for toast type.

        Args:
            toast_type: Toast notification type

        Returns:
            Display duration in milliseconds
        """
        durations = {
            ToastType.SUCCESS: self.DURATION_SUCCESS,
            ToastType.ERROR: self.DURATION_ERROR,
            ToastType.INFO: self.DURATION_INFO,
            ToastType.WARNING: self.DURATION_WARNING,
        }
        return durations.get(toast_type, self.DURATION_INFO)


# Global instance for easy access
DEFAULT_CONFIG: Final[ToastConfig] = ToastConfig()
