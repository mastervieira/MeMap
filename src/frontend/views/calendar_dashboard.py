"""
Componente de Calendário Customizado para o MeMap Pro.
Implementa células interativas e design moderno.
"""

from PySide6.QtCore import Qt, Signal, Slot, QDate, QRect
from PySide6.QtWidgets import QCalendarWidget, QWidget, QVBoxLayout, QFrame
from PySide6.QtGui import QColor, QPen, QBrush, QFont, QPainter

from src.frontend.styles.component_styles import CalendarWidgetStyles

class CustomCalendarWidget(QCalendarWidget):
    """Calendário com células customizadas e interativas."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setGridVisible(False)
        self.setNavigationBarVisible(True)
        self.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)

        # Estilo base via QSS
        self.setStyleSheet(CalendarWidgetStyles.get_calendar_style())

    def paintCell(self, painter: QPainter, rect: QRect, date: QDate):
        """Customiza a renderização de cada célula do calendário."""
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Cores baseadas no estado da célula
        is_selected = date == self.selectedDate()
        is_today = date == QDate.currentDate()
        is_current_month = date.month() == self.monthShown()

        # Fundo da célula
        if is_selected:
            painter.setBrush(QBrush(QColor("#007ACC"))) # Accent color
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)
        elif is_today:
            painter.setPen(QPen(QColor("#007ACC"), 2))
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)

        # Texto do dia
        if is_selected:
            painter.setPen(QColor("#FFFFFF"))
        elif is_current_month:
            painter.setPen(QColor("#CCCCCC"))
        else:
            painter.setPen(QColor("#555555")) # Dias de outros meses

        font = painter.font()
        font.setBold(is_selected or is_today)
        painter.setFont(font)

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))

        painter.restore()

class CalendarDashboard(QFrame):
    """Dashboard que contém o calendário e emite sinais de interação."""

    date_selected = Signal(QDate)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("calendar_dashboard_container")

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        self.calendar = CustomCalendarWidget()
        self.calendar.clicked.connect(self._on_date_clicked)

        self.main_layout.addWidget(self.calendar)

    @Slot(QDate)
    def _on_date_clicked(self, date: QDate):
        """Emitido quando uma célula (dia) é clicada."""
        self.date_selected.emit(date)
