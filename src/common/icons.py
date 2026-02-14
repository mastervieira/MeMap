"""
Gerenciador de ícones do MeMap Pro com integração ao tema.
Usa QtAwesome para ícones vetoriais modernos.
"""

from PySide6.QtGui import QIcon
import qtawesome as qta

from src.common.themes import ThemeManager, Theme


class IconManager:
    """Gerencia ícones da aplicação com suporte a temas."""

    def __init__(self):
        self.theme_manager = ThemeManager()

    def _get_icon_color(self) -> str:
        """Retorna a cor do ícone baseada no tema atual."""
        palette = self.theme_manager.current_palette
        return palette.text_primary

    def _get_accent_color(self) -> str:
        """Retorna a cor de destaque baseada no tema atual."""
        palette = self.theme_manager.current_palette
        return palette.accent

    # Ícones do Sidebar
    def dashboard(self) -> QIcon:
        """Ícone do Dashboard."""
        return qta.icon('fa5s.home', color=self._get_icon_color())

    def wizard(self) -> QIcon:
        """Ícone do Wizard/Formulário."""
        return qta.icon('fa5s.edit', color=self._get_icon_color())

    def calendar(self) -> QIcon:
        """Ícone do Calendário."""
        return qta.icon('fa5s.calendar-alt', color=self._get_icon_color())

    def tasks(self) -> QIcon:
        """Ícone de Tarefas."""
        return qta.icon('fa5s.tasks', color=self._get_icon_color())

    def analytics(self) -> QIcon:
        """Ícone de Análises."""
        return qta.icon('fa5s.chart-line', color=self._get_icon_color())

    def settings(self) -> QIcon:
        """Ícone de Configurações."""
        return qta.icon('fa5s.cog', color=self._get_icon_color())

    # Ícones de ação
    def sun(self) -> QIcon:
        """Ícone do Sol (tema light)."""
        return qta.icon('fa5s.sun', color=self._get_accent_color())

    def moon(self) -> QIcon:
        """Ícone da Lua (tema dark)."""
        return qta.icon('fa5s.moon', color=self._get_accent_color())

    def save(self) -> QIcon:
        """Ícone de Salvar."""
        return qta.icon('fa5s.save', color=self._get_icon_color())

    def export(self) -> QIcon:
        """Ícone de Exportar."""
        return qta.icon('fa5s.file-export', color=self._get_icon_color())

    def refresh(self) -> QIcon:
        """Ícone de Atualizar."""
        return qta.icon('fa5s.sync-alt', color=self._get_icon_color())

    def search(self) -> QIcon:
        """Ícone de Pesquisa."""
        return qta.icon('fa5s.search', color=self._get_icon_color())

    # Ícones de status
    def success(self) -> QIcon:
        """Ícone de Sucesso."""
        palette = self.theme_manager.current_palette
        return qta.icon('fa5s.check-circle', color=palette.success)

    def error(self) -> QIcon:
        """Ícone de Erro."""
        palette = self.theme_manager.current_palette
        return qta.icon('fa5s.times-circle', color=palette.error)

    def warning(self) -> QIcon:
        """Ícone de Aviso."""
        palette = self.theme_manager.current_palette
        return qta.icon('fa5s.exclamation-triangle', color=palette.warning)

    def info(self) -> QIcon:
        """Ícone de Informação."""
        palette = self.theme_manager.current_palette
        return qta.icon('fa5s.info-circle', color=palette.info)
