"""ViewModel para a MainView.

Gerencia:
- Navegação entre páginas da aplicação
- Gestão de tema (claro/escuro)
- Estado global da aplicação
"""

from __future__ import annotations

import logging
from typing import Literal

from PySide6.QtCore import Signal

from src.common.themes import Theme, ThemeManager
from src.frontend.viewmodels.base_view_model import BaseViewModel

logger: logging.Logger = logging.getLogger(__name__)

PageType = Literal[
    "dashboard", "wizard", "calendar", "tasks", "analytics", "settings"]


class MainViewModel(BaseViewModel):
    """ViewModel para navegação e estado global da aplicação."""

    # Sinais
    current_page_changed = Signal(str)  # Nome da página
    theme_changed = Signal(object)  # Theme enum

    def __init__(self) -> None:
        """Inicializa o MainViewModel."""
        super().__init__()
        self._current_page: PageType = "dashboard"
        self._theme_manager = ThemeManager()

    def on_appear(self) -> None:
        """Chamado quando a MainView é ativada."""
        logger.info("MainView apareceu na tela")

    # ==================== NAVEGAÇÃO ====================

    def navigate_to(self, page: PageType) -> None:
        """Navega para uma página específica.

        Args:
            page: Nome da página para navegar
        """
        if page != self._current_page:
            old_page = self._current_page
            self._current_page = page
            self.current_page_changed.emit(page)
            logger.info(f"Navegação: {old_page} → {page}")

    def get_current_page(self) -> PageType:
        """Retorna página atual.

        Returns:
            Nome da página atual
        """
        return self._current_page

    def can_navigate_to(self, page: PageType) -> bool:
        """Verifica se pode navegar para uma página.

        Args:
            page: Nome da página

        Returns:
            True se navegação é permitida
        """
        # TODO: Implementar lógica de permissões/restrições
        # Por enquanto permite tudo
        valid_pages: list[PageType] = [
            "dashboard",
            "wizard",
            "calendar",
            "tasks",
            "analytics",
            "settings"
        ]
        return page in valid_pages

    # ==================== TEMA ====================

    def toggle_theme(self) -> None:
        """Alterna entre tema claro e escuro."""
        current_theme: Theme = self._theme_manager.current_theme

        if current_theme == Theme.LIGHT:
            self.set_theme(Theme.DARK)
        else:
            self.set_theme(Theme.LIGHT)

    def set_theme(self, theme: Theme) -> None:
        """Define tema da aplicação.

        Args:
            theme: Tema a aplicar (LIGHT ou DARK)
        """
        if theme != self._theme_manager.current_theme:
            self._theme_manager.set_theme(theme)
            self.theme_changed.emit(theme)
            logger.info(f"Tema alterado para: {theme.name}")

    def get_current_theme(self) -> Theme:
        """Retorna tema atual.

        Returns:
            Tema atual
        """
        return self._theme_manager.current_theme

    def get_theme_manager(self) -> ThemeManager:
        """Retorna o gerenciador de temas.

        Returns:
            ThemeManager instance
        """
        return self._theme_manager

    # ==================== LIFECYCLE ====================

    def dispose(self) -> None:
        """Limpa recursos."""
        logger.info("MainViewModel foi descartado")
