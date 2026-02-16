# type: ignore
"""Toast notification widget module."""

from typing import Callable

import qtawesome as qta
from PySide6.QtWidgets import (
    QWidget,
    QLabel,
    QHBoxLayout,
    QGraphicsDropShadowEffect,
    QFrame,
    QPushButton
    )
from PySide6.QtCore import (
    Qt,
    QPropertyAnimation,
    QTimer,
    Signal,
    QPoint,
    )
from PySide6.QtGui import QColor, QPixmap

from src.common.themes.colors import ColorPalette
from src.common.themes.theme_manager import ThemeManager
from .toast_config import CloseReason, ToastType, DEFAULT_CONFIG


class ModernToast(QFrame):
    """Modern toast notification widget with smooth animations and theme support."""

    closed = Signal(object, CloseReason)  # Emits (self, close_reason)

    def __init__(
            self,
            parent: QWidget,
            message: str,
            toast_type: ToastType,
            duration: int | None = None,
            ) -> None:
        """Initialize the toast notification widget.

        Args:
            parent: Parent widget
            message: Notification message text
            toast_type: Toast notification type (SUCCESS, ERROR, INFO, WARNING)
            duration: Display duration in milliseconds (None uses type-specific default)
        """
        super().__init__(parent)

        # Storage for animations and theme callback
        self.slide_anim: QPropertyAnimation | None = None
        self._theme_callback: Callable[[], None] | None = None
        self.toast_type: ToastType = toast_type
        self.message: str = message

        # Setup Dimensional
        self.setFixedWidth(DEFAULT_CONFIG.WIDTH)
        self.setMinimumHeight(DEFAULT_CONFIG.MIN_HEIGHT)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)  # Memory cleanup

        # Get theme colors
        self.theme_manager = ThemeManager()
        palette: ColorPalette = self.theme_manager.current_palette

        # Get type-specific configuration
        type_config: dict[str, str] = self._get_type_config()
        border_color: str = type_config["color"]

        # Design System with theme-aware colors
        self.setStyleSheet(f"""
            QFrame#ToastContainer {{
                background-color: {palette.background_secondary};
                border-left: 4px solid {border_color};
                border-radius: 6px;
            }}
            QLabel#MessageLabel {{
                color: {palette.text_primary};
                font-size: 12px;
                font-family: "Segoe UI", "Arial";
            }}
            QPushButton#CloseButton {{
                background: transparent;
                border: none;
                color: {palette.text_secondary};
            }}
            QPushButton#CloseButton:hover {{
                color: {palette.text_primary};
            }}
        """)
        self.setObjectName("ToastContainer")

        # Drop shadow effect
        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        self.setGraphicsEffect(shadow)

        # Main layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 8, 12)
        main_layout.setSpacing(10)

        # Icon label initialization
        self.icon_label: QLabel = QLabel()
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        icon_pixmap: QPixmap = qta.icon(
            type_config["icon"], color=border_color
            ).pixmap(20, 20)
        self.icon_label.setPixmap(icon_pixmap)

        # Message label initialization
        self.msg_label: QLabel = QLabel(message)
        self.msg_label.setObjectName("MessageLabel")
        self.msg_label.setWordWrap(True)
        self.msg_label.setAlignment(Qt.AlignmentFlag.AlignVCenter)

        # Close button initialization
        self.close_btn: QPushButton = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setIcon(
            qta.icon("fa5s.times", color=palette.text_secondary))
        self.close_btn.setFixedSize(20, 20)
        self.close_btn.clicked.connect(
            lambda: self.fade_out(CloseReason.MANUAL))

        main_layout.addWidget(self.icon_label)
        main_layout.addWidget(self.msg_label, 1)
        main_layout.addWidget(self.close_btn)

        # Auto-close timer initialization
        self.timer: QTimer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(lambda: self.fade_out(CloseReason.AUTO))

        # Set display duration
        if duration is None:
            duration = DEFAULT_CONFIG.get_duration_for_type(toast_type)
        self.duration: int = duration

        # Register theme callback to rebuild stylesheet on theme change
        self._register_theme_callback()

    def _get_type_config(self) -> dict[str, str]:
        """Get icon and color configuration for toast type.

        Returns:
            Dictionary with 'icon' and 'color' keys
        """
        palette: ColorPalette = self.theme_manager.current_palette
        configs: dict[ToastType, dict[str, str]] = {
            ToastType.SUCCESS: {
                "icon": "fa5s.check-circle", "color": palette.success},
            ToastType.ERROR: {
                "icon": "fa5s.exclamation-triangle", "color": palette.error},
            ToastType.INFO: {
                "icon": "fa5s.info-circle", "color": palette.info},
            ToastType.WARNING: {
                "icon": "fa5s.exclamation-circle", "color": palette.warning},
        }
        return configs.get(self.toast_type, configs[ToastType.INFO])

    def _register_theme_callback(self) -> None:
        """Register callback for theme changes to update colors dynamically."""
        def on_theme_changed() -> None:
            """Update toast colors when theme changes."""
            palette: ColorPalette = self.theme_manager.current_palette
            type_config: dict[str, str] = self._get_type_config()
            border_color: str = type_config["color"]

            self.setStyleSheet(f"""
                QFrame#ToastContainer {{
                    background-color: {palette.background_secondary};
                    border-left: 4px solid {border_color};
                    border-radius: 6px;
                }}
                QLabel#MessageLabel {{
                    color: {palette.text_primary};
                    font-size: 12px;
                    font-family: "Segoe UI", "Arial";
                }}
                QPushButton#CloseButton {{
                    background: transparent;
                    border: none;
                    color: {palette.text_secondary};
                }}
                QPushButton#CloseButton:hover {{
                    color: {palette.text_primary};
                }}
            """)

            # Update close button icon color
            self.close_btn.setIcon(qta.icon(
                "fa5s.times", color=palette.text_secondary))

        self._theme_callback = on_theme_changed
        self.theme_manager.register_callback(on_theme_changed)

    def show_animated(self, target_pos: QPoint) -> None:
        """Display toast with smooth slide-in animation.

        Args:
            target_pos: Target position for the toast widget
        """
        self.move(target_pos)
        self.show()

        # Slide animation from right
        self.slide_anim = QPropertyAnimation(self, b"pos")
        self.slide_anim.setDuration(DEFAULT_CONFIG.SLIDE_IN_DURATION)
        self.slide_anim.setStartValue(target_pos + QPoint(DEFAULT_CONFIG.SLIDE_OFFSET, 0))
        self.slide_anim.setEndValue(target_pos)
        self.slide_anim.setEasingCurve(DEFAULT_CONFIG.SLIDE_EASING)
        self.slide_anim.start()

        self.timer.start(self.duration)

    def fade_out(self, reason: CloseReason = CloseReason.AUTO) -> None:
        """Close toast and emit closed signal.

        Args:
            reason: Reason for closure (AUTO, MANUAL, PROGRAMMATIC)
        """
        self.timer.stop()
        self.cleanup()
        self.closed.emit(self, reason)
        self.deleteLater()

    def cleanup(self) -> None:
        """Clean up resources before deletion.

        Unregisters theme callbacks, stops timers, and cancels animations.
        """
        # Unregister theme callback
        if self._theme_callback is not None:
            self.theme_manager.unregister_callback(self._theme_callback)  # type: ignore
            self._theme_callback = None

        # Stop timer
        self.timer.stop()

        # Cancel animations
        if self.slide_anim is not None:
            self.slide_anim.stop()
            self.slide_anim = None

    def cancel_animations(self) -> None:
        """Cancel any running animations."""
        if self.slide_anim is not None:
            self.slide_anim.stop()
            self.slide_anim = None
