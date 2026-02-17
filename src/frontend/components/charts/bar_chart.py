"""
Componente de gráfico de barras verticais usando PyQtGraph.
"""

from typing import Literal

import pyqtgraph as pg  # type: ignore
from PySide6.QtWidgets import QVBoxLayout

from src.common.themes import ThemeManager
from src.frontend.components.charts.base_chart import BaseChart


class VerticalBarChart(BaseChart):
    """Gráfico de barras verticais para comparação de valores."""

    def __init__(
        self,
        parent: BaseChart | None = None,
        theme_manager: ThemeManager | None = None,
        title: str = "",
    ) -> None:
        """Inicializa o gráfico de barras verticais.

        Args:
            parent: Widget pai
            theme_manager: Gerenciador de temas
            title: Título do gráfico
        """
        super().__init__(parent, theme_manager)
        self.title: str = title
        self._data: dict[str, float] = {}
        self._bar_items: list[pg.BarGraphItem] = []

        self._init_ui()

    def _init_ui(self) -> None:
        """Inicializa a interface do gráfico."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Cria o plot widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setMinimumHeight(120)
        self.plot_widget.setMaximumHeight(150)

        # Remove padding extra
        self.plot_widget.getPlotItem().setContentsMargins(5, 5, 5, 5)

        # Oculta eixo inferior (x)
        self.plot_widget.getPlotItem().hideAxis("bottom")

        # Configura eixo esquerdo (y) para valores monetários
        self.plot_widget.setLabel("left", "Valor (€)")

        # Remove menus de contexto
        self.plot_widget.setMenuEnabled(False)

        # Desabilita interação de mouse
        self.plot_widget.setMouseEnabled(x=False, y=False)

        layout.addWidget(self.plot_widget)

        # Aplica tema inicial
        self._apply_theme_to_plot()

    def set_data(self, premio: float, gastos: float) -> None:
        """Define os dados do gráfico.

        Args:
            premio: Valor do prémio em euros
            gastos: Valor dos gastos em euros
        """
        self._data = {"Prémio": premio, "Gastos": gastos}
        self._update_chart_data()

    def _update_chart_data(self) -> None:
        """Atualiza o gráfico com os dados atuais."""
        if not self.plot_widget or not self._data:
            return

        # Limpa barras anteriores
        for item in self._bar_items:
            self.plot_widget.removeItem(item)
        self._bar_items.clear()

        # Prepara dados
        premio: float = self._data.get("Prémio", 0.0)
        gastos: float = self._data.get("Gastos", 0.0)

        # Posições das barras (x)
        x_positions: list[int] = [0, 1]
        heights: list[float] = [premio, gastos]

        # Cores das barras
        colors: list[str] = [
            self.style_manager.colors.success,  # Verde para prémio
            self.style_manager.colors.danger,  # Vermelho para gastos
        ]

        # Cria as barras
        for i, (x, height, color) in enumerate(zip(x_positions, heights, colors)):
            if height > 0:
                bar = pg.BarGraphItem(
                    x=[x],
                    height=[height],
                    width=0.6,
                    brush=color,
                    pen={"color": self.style_manager.get_text_color(), "width": 1},
                )
                self.plot_widget.addItem(bar)
                self._bar_items.append(bar)

                # Adiciona label de valor acima da barra
                text_item = pg.TextItem(
                    text=f"€{height:.2f}".replace(".", ","),
                    color=self.style_manager.get_text_color(),
                    anchor=(0.5, 1.2),
                )
                text_item.setPos(x, height)
                self.plot_widget.addItem(text_item)
                self._bar_items.append(text_item)

        # Adiciona labels das categorias abaixo das barras
        labels: list[str] = ["💶 Prémio", "💸 Gastos"]
        for i, (x, label) in enumerate(zip(x_positions, labels)):
            text_item = pg.TextItem(
                text=label,
                color=self.style_manager.get_text_color(),
                anchor=(0.5, -0.5),
            )
            text_item.setPos(x, 0)
            self.plot_widget.addItem(text_item)
            self._bar_items.append(text_item)

        # Ajusta range do gráfico
        max_value: float | Literal[10] = max(premio, gastos) if max(premio, gastos) > 0 else 10
        self.plot_widget.setXRange(-0.5, 1.5, padding=0.1)
        self.plot_widget.setYRange(0, max_value * 1.3, padding=0.05)

        # Reaplica tema
        self._apply_theme_to_plot()
