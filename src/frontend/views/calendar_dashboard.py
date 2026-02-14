# type: ignore
"""
Componente de Calendário Customizado para o MeMap Pro.
Implementa células interativas e design moderno.
"""
from PySide6.QtCore import QDate, QRect, Qt, Signal, Slot
from PySide6.QtGui import QBrush, QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QCalendarWidget, QFrame, QVBoxLayout

from src.frontend.styles.component_styles import CalendarWidgetStyles
from src.common.themes import ThemeManager


class CustomCalendarWidget(QCalendarWidget):
    """Calendário com células customizadas e interativas."""

    def __init__(self, viewmodel=None, parent=None) -> None:
        """Inicializa o calendário com ViewModel.

        Args:
            viewmodel: CalendarViewModel para gerenciar estados dos dias
            parent: Widget pai
        """
        super().__init__(parent)
        self.setGridVisible(False)
        self.setNavigationBarVisible(True)
        self.setVerticalHeaderFormat(
            QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader
            )

        # FASE 3.2: ViewModel para estados dos dias
        self._viewmodel = viewmodel

        # Theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.register_callback(self._apply_theme)

        # FASE 3.2: Conectar signal do ViewModel para atualizar células
        if self._viewmodel:
            self._viewmodel.day_states_updated.connect(self.updateCells)

        # Estilo base via QSS
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Aplica o tema atual ao calendário."""
        self.setStyleSheet(CalendarWidgetStyles.get_calendar_style())
        self.update()  # Força redesenho das células

    def paintCell(self, painter: QPainter, rect: QRect, date: QDate) -> None:
        """Customiza a renderização de cada célula do calendário.

        FASE 3.2: Agora usa CalendarViewModel para determinar cores dos dias:
        - Verde: dia salvo na BD
        - Amarelo: dia modificado mas não salvo
        """
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Obtém cores do tema atual
        palette = self.theme_manager.current_palette

        # Estados da célula
        is_selected = date == self.selectedDate()
        is_today = date == QDate.currentDate()
        is_current_month = date.month() == self.monthShown()

        # FASE 3.2: Obter cor do estado (verde/amarelo) do ViewModel
        state_color = None
        if self._viewmodel:
            state_color = self._viewmodel.get_day_color(date)

        # Desenhar fundo da célula
        if state_color:
            # Dia com estado (salvo/modificado)
            painter.setBrush(QBrush(state_color))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)
        elif is_selected:
            # Dia selecionado
            painter.setBrush(QBrush(QColor(palette.accent)))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)
        elif is_today and is_current_month:
            # Dia de hoje
            painter.setBrush(QBrush(QColor(palette.surface_hover)))
            painter.setPen(QPen(QColor(palette.accent), 2))
            painter.drawRoundedRect(rect.adjusted(2, 2, -2, -2), 8, 8)

        # Texto do dia
        if is_selected:
            painter.setPen(QColor("#FFFFFF"))  # Branco para contraste
        elif is_current_month:
            painter.setPen(QColor(palette.text_primary))
        else:
            painter.setPen(QColor(palette.text_disabled))

        font: QFont = painter.font()
        font.setBold(is_selected or is_today)
        painter.setFont(font)

        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, str(date.day()))

        painter.restore()

class CalendarDashboard(QFrame):
    """Dashboard que contém o calendário e emite sinais de interação."""

    date_selected = Signal(QDate)

    def __init__(self, viewmodel=None, parent=None) -> None: # type: ignore
        """Inicializa o CalendarDashboard.

        Args:
            viewmodel: CalendarViewModel para gerenciar estados dos dias
            parent: Widget pai
        """
        super().__init__(parent)
        self.setObjectName("calendar_dashboard_container")

        # FASE 3.2: Armazenar ViewModel
        self._viewmodel = viewmodel

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)

        # FASE 3.2: Passar ViewModel ao CustomCalendarWidget
        self.calendar = CustomCalendarWidget(viewmodel=viewmodel)
        self.calendar.clicked.connect(self._on_date_clicked)

        self.main_layout.addWidget(self.calendar)

    @Slot(QDate)
    def _on_date_clicked(self, date: QDate) -> None:
        """Emitido quando uma célula (dia) é clicada."""
        self.date_selected.emit(date)
