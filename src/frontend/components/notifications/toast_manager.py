# type: ignore
"""Notification manager for displaying toast messages."""

import time

from PySide6.QtCore import QObject, QPoint, QPropertyAnimation
from PySide6.QtWidgets import QWidget

from .toast_config import CloseReason, ToastType, DEFAULT_CONFIG
from .toast_widget import ModernToast


class NotificationManager(QObject):
    """Singleton manager for displaying toast notifications with advanced features.

    Handles creation, positioning, lifecycle, deduplication,
      and limits of toast notifications.
    Supports success, error, info, and warning notification types.
    """

    _instance: "NotificationManager | None" = None

    def __init__(self, main_window: QWidget | None = None) -> None:
        """Initialize the notification manager.

        Args:
            main_window: Parent widget for toast notifications
        """
        super().__init__()
        self.main_window: QWidget | None = main_window
        self.active_toasts: list[ModernToast] = []
        self.margin: int = DEFAULT_CONFIG.MARGIN
        self.spacing: int = DEFAULT_CONFIG.SPACING
        self.max_toasts: int = DEFAULT_CONFIG.MAX_TOASTS

        # Deduplication
        self.recent_messages: dict[str, float] = {}
        self.dedup_enabled: bool = True

        # Pause/resume functionality
        self.paused: bool = False

        # Animation tracking
        self.pending_animations: list[QPropertyAnimation] = []

    @classmethod
    def instance(
        cls, main_window: QWidget | None = None) -> "NotificationManager":
        """Get or create the singleton instance.

        Args:
            main_window: Parent widget for toast notifications

        Returns:
            The singleton NotificationManager instance
        """
        if cls._instance is None:
            cls._instance = NotificationManager(main_window)
        return cls._instance

    def success(
            self, message: str, duration: int | None = None
            ) -> ModernToast | None:
        """Display a success notification.

        Args:
            message: Notification message text
            duration: Custom display duration (None uses type-specific default)

        Returns:
            The created toast widget, or None if deduplicated
        """
        return self._create_toast(message, ToastType.SUCCESS, duration)

    def error(
            self, message: str, duration: int | None = None
            ) -> ModernToast | None:
        """Display an error notification.

        Args:
            message: Notification message text
            duration: Custom display duration (None uses type-specific default)

        Returns:
            The created toast widget, or None if deduplicated
        """
        return self._create_toast(message, ToastType.ERROR, duration)

    def info(
            self, message: str, duration: int | None = None
            ) -> ModernToast | None:
        """Display an info notification.

        Args:
            message: Notification message text
            duration: Custom display duration (None uses type-specific default)

        Returns:
            The created toast widget, or None if deduplicated
        """
        return self._create_toast(message, ToastType.INFO, duration)

    def warning(
            self, message: str, duration: int | None = None
            ) -> ModernToast | None:
        """Display a warning notification.

        Args:
            message: Notification message text
            duration: Custom display duration (None uses type-specific default)

        Returns:
            The created toast widget, or None if deduplicated
        """
        return self._create_toast(message, ToastType.WARNING, duration)

    def _create_toast(
            self, message: str,
            toast_type: ToastType,
            duration: int | None = None
            ) -> ModernToast | None:
        """Create and display a new toast notification.

        Args:
            message: Notification message text
            toast_type: Toast notification type
            duration: Custom display duration (None uses type-specific default)

        Returns:
            The created toast widget, or None if deduplicated or at max limit

        Raises:
            RuntimeError: If main_window is not set
        """
        if self.main_window is None:
            raise RuntimeError(
                "NotificationManager requires a main_window to be set")

        # Check for duplicate messages
        if self.dedup_enabled and self._is_duplicate(message):
            return None

        # Enforce maximum toast limit
        if len(self.active_toasts) >= self.max_toasts:
            self._remove_oldest_toast()

        # Create toast widget
        toast = ModernToast(self.main_window, message, toast_type, duration)
        toast.closed.connect(self._on_toast_closed)

        self.active_toasts.append(toast)
        self.recent_messages[message] = time.time()
        self._cleanup_old_dedup_entries()

        self._reposition_toasts()
        toast.show_animated(toast.pos())

        return toast

    def _is_duplicate(self, message: str) -> bool:
        """Check if message was recently displayed.

        Args:
            message: Message to check

        Returns:
            True if message is a recent duplicate
        """
        if message not in self.recent_messages:
            return False

        time_elapsed: float = time.time() - self.recent_messages[message]
        return time_elapsed < (DEFAULT_CONFIG.DEDUP_WINDOW_MS / 1000.0)

    def _cleanup_old_dedup_entries(self) -> None:
        """Remove expired entries from deduplication cache."""
        current_time: float = time.time()
        expired = []

        for message, timestamp in self.recent_messages.items():
            if current_time - timestamp > (
                DEFAULT_CONFIG.DEDUP_WINDOW_MS / 1000.0):
                expired.append(message)

        for message in expired:
            del self.recent_messages[message]

    def _remove_oldest_toast(self) -> None:
        """Remove the oldest active toast when limit is reached."""
        if self.active_toasts:
            oldest_toast: ModernToast = self.active_toasts[0]
            oldest_toast.fade_out(CloseReason.PROGRAMMATIC)

    def _reposition_toasts(self, start_index: int = 0) -> None:
        """Reposition active toasts in a vertical stack.

        Positions toasts in the bottom-right corner, stacking upwards.
        Only repositions toasts from the given start_index onwards (optimization).

        Args:
            start_index: Index to start repositioning from
        """
        if not self.main_window:
            return

        for i, toast in enumerate(self.active_toasts):
            if i < start_index:
                continue

            dest_x: int = self.main_window.width() \
                - toast.width() - self.margin
            dest_y: int = self.main_window.height() \
                - ((i + 1) * (toast.height() + self.spacing)) - self.margin

            if toast.isVisible():
                self._animate_move(toast, QPoint(dest_x, dest_y))
            else:
                toast.move(dest_x, dest_y)

    def _animate_move(self, widget: ModernToast, new_pos: QPoint) -> None:
        """Animate a toast to a new position.

        Cancels any existing animation before starting a new one.

        Args:
            widget: Toast widget to animate
            new_pos: Target position
        """
        # Cancel existing animation if present
        if hasattr(widget, '_move_anim') and widget._move_anim is not None:
            widget._move_anim.stop()  # type: ignore

        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(DEFAULT_CONFIG.REPOSITION_DURATION)
        anim.setEndValue(new_pos)
        anim.setEasingCurve(DEFAULT_CONFIG.REPOSITION_EASING)
        anim.start()

        # Keep reference to prevent garbage collection
        widget._move_anim = anim  # type: ignore
        self.pending_animations.append(anim)

        # Clean up finished animations
        anim.finished.connect(lambda: self._cleanup_animation(anim))

    def _cleanup_animation(self, anim: QPropertyAnimation) -> None:
        """Remove animation from tracking list after completion.

        Args:
            anim: Completed animation
        """
        if anim in self.pending_animations:
            self.pending_animations.remove(anim)

    def _on_toast_closed(self, toast: ModernToast, reason: CloseReason) -> None:
        """Handle toast closure and reposition remaining toasts.

        Args:
            toast: The closed toast widget
            reason: Reason for closure
        """
        if toast in self.active_toasts:
            index: int = self.active_toasts.index(toast)
            self.active_toasts.remove(toast)
            # Only reposition toasts that were below the removed one
            self._reposition_toasts(start_index=index)

    def clear_all(self) -> None:
        """Close all active toasts with PROGRAMMATIC reason."""
        # Create a copy since closing modifies the list
        toasts_to_close: list[ModernToast] = self.active_toasts.copy()
        for toast in toasts_to_close:
            toast.fade_out(CloseReason.PROGRAMMATIC)

    def pause_all(self) -> None:
        """Pause all toast timers."""
        if self.paused:
            return

        self.paused = True
        for toast in self.active_toasts:
            if toast.timer.isActive():
                remaining_time = toast.timer.remainingTime()
                toast.timer.stop()
                # Store remaining time for resume
                toast._remaining_time = remaining_time  # type: ignore

    def resume_all(self) -> None:
        """Resume all paused toast timers."""
        if not self.paused:
            return

        self.paused = False
        for toast in self.active_toasts:
            if hasattr(toast, '_remaining_time'):
                remaining_time: int = int(toast._remaining_time)
                if remaining_time > 0:
                    toast.timer.start(remaining_time)
                del toast._remaining_time  # type: ignore
            else:
                # If we don't know remaining time, use full duration
                toast.timer.start(toast.duration)

    def get_active_count(self) -> int:
        """Get number of active toasts.

        Returns:
            Count of currently displayed toasts
        """
        return len(self.active_toasts)

    def set_max_toasts(self, max_count: int) -> None:
        """Configure maximum simultaneous toasts.

        Args:
            max_count: Maximum number of simultaneous toasts
        """
        if max_count < 1:
            raise ValueError("max_toasts must be at least 1")

        self.max_toasts = max_count

        # Remove excess toasts if current count exceeds new limit
        while len(self.active_toasts) > self.max_toasts:
            self._remove_oldest_toast()

    def set_deduplication(self, enabled: bool) -> None:
        """Enable or disable message deduplication.

        Args:
            enabled: True to enable deduplication
        """
        self.dedup_enabled = enabled
        if not enabled:
            self.recent_messages.clear()
