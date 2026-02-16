"""Toast notification components package.

This module provides a modern, feature-rich toast notification system with:
- Multiple notification types (success, error, info, warning)
- Type-specific display durations
- Message deduplication
- Maximum toast limit with FIFO removal
- Pause/resume functionality
- Theme-aware colors
- Smooth animations

Example usage:
    ```python
    from src.frontend.components.notifications import NotificationManager

    # Initialize with main window
    notif_manager = NotificationManager.instance(main_window)

    # Show notifications
    notif_manager.success("Operation completed!")
    notif_manager.error("An error occurred")
    notif_manager.info("Processing...")
    notif_manager.warning("This is a warning")

    # Control notifications
    notif_manager.clear_all()
    notif_manager.pause_all()
    notif_manager.resume_all()

    # Configure behavior
    notif_manager.set_max_toasts(3)
    notif_manager.set_deduplication(True)
    ```
"""

from .toast_manager import NotificationManager
from .toast_widget import ModernToast
from .toast_config import ToastConfig, CloseReason, ToastType

__all__ = [
    'NotificationManager',
    'ModernToast',
    'ToastConfig',
    'CloseReason',
    'ToastType',
]
