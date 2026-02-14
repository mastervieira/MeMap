"""
Estilos e configurações para gráficos PyQtGraph.
Gerencia cores, fontes e aparência baseado no tema atual.
"""

from dataclasses import dataclass

from src.common.themes import ThemeManager
from src.common.themes.colors import ColorPalette


@dataclass
class ChartColors:
    """Cores padrão para gráficos."""

    # Cores de dados
    success: str = "#28a745"  # Verde para valores positivos
    danger: str = "#dc3545"  # Vermelho para valores negativos
    primary: str = "#0078D4"  # Azul primário
    warning: str = "#ffc107"  # Amarelo para avisos
    info: str = "#17a2b8"  # Ciano para informação

    # Cores de gastos específicos
    gasoleo_color: str = "#ff6b6b"  # Vermelho claro
    almoco_color: str = "#4ecdc4"  # Verde-azulado
    despesas_color: str = "#95e1d3"  # Verde claro


class ChartStyleManager:
    """Gerencia estilos de gráficos baseado no tema atual."""

    def __init__(self, theme_manager: ThemeManager | None = None) -> None:
        """Inicializa o gerenciador de estilos.

        Args:
            theme_manager: Instância do ThemeManager. Se None, cria uma nova.
        """
        self.theme_manager = theme_manager or ThemeManager()
        self.colors = ChartColors()

    @property
    def palette(self) -> ColorPalette:
        """Retorna a paleta de cores do tema atual."""
        return self.theme_manager.current_palette

    def get_background_color(self) -> str:
        """Retorna a cor de fundo para gráficos."""
        return self.palette.background_secondary

    def get_text_color(self) -> str:
        """Retorna a cor de texto para gráficos."""
        return self.palette.text_primary

    def get_grid_color(self) -> str:
        """Retorna a cor das linhas de grade."""
        # Cor da borda com transparência reduzida
        return self.palette.border

    def get_axis_pen(self) -> dict:
        """Retorna configuração de caneta para eixos."""
        return {"color": self.palette.text_primary, "width": 1}

    def get_grid_pen(self) -> dict:
        """Retorna configuração de caneta para grade."""
        return {"color": self.palette.border, "width": 1, "style": 1}  # style 1 = dotted

    def get_bar_brush(self, color: str) -> str:
        """Retorna a cor de preenchimento para barras.

        Args:
            color: Cor em formato hex (#RRGGBB)

        Returns:
            Cor em formato hex
        """
        return color
