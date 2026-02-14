"""
Classe base para todos os componentes de gráficos.
Fornece funcionalidade comum e integração com temas.
"""

import pyqtgraph as pg  # type: ignore
from PySide6.QtWidgets import QWidget

from src.common.themes import ThemeManager
from src.frontend.components.charts.chart_styles import ChartStyleManager


class BaseChart(QWidget):
    """Classe base para gráficos PyQtGraph com suporte a temas."""

    def __init__(
        self, parent: QWidget | None = None, theme_manager: ThemeManager | None = None
    ) -> None:
        """Inicializa o gráfico base.

        Args:
            parent: Widget pai
            theme_manager: Gerenciador de temas. Se None, cria uma nova instância.
        """
        super().__init__(parent)
        self.theme_manager = theme_manager or ThemeManager()
        self.style_manager = ChartStyleManager(self.theme_manager)

        # Registra callback para mudanças de tema
        self.theme_manager.register_callback(self._on_theme_changed)

        # PlotWidget será criado pelas subclasses
        self.plot_widget: pg.PlotWidget | None = None

    def _apply_theme_to_plot(self) -> None:
        """Aplica o tema atual ao plot widget."""
        if not self.plot_widget:
            return

        # Define cor de fundo
        self.plot_widget.setBackground(self.style_manager.get_background_color())

        # Obtém os eixos
        axis_items = self.plot_widget.getPlotItem().axes

        # Aplica cor de texto aos eixos
        for axis_name, axis_data in axis_items.items():
            axis_item = axis_data["item"]
            axis_item.setTextPen(self.style_manager.get_text_color())
            axis_item.setPen(self.style_manager.get_axis_pen())

        # Configura grade
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)

    def _on_theme_changed(self) -> None:
        """Callback chamado quando o tema muda."""
        self._apply_theme_to_plot()
        self._update_chart_data()

    def _update_chart_data(self) -> None:
        """Atualiza os dados do gráfico. Deve ser implementado pelas subclasses."""
        raise NotImplementedError("Subclasses devem implementar _update_chart_data")
