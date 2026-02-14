"""
Gerenciador de temas para o MeMap Pro.
Centraliza o gerenciamento e aplicação de temas na aplicação.
"""

import json
from enum import Enum
from pathlib import Path
from typing import Final

from src.common.themes.colors import DARK_THEME, LIGHT_THEME, ColorPalette


class Theme(Enum):
    """Temas disponíveis."""
    DARK = "dark"
    LIGHT = "light"


class ThemeManager:
    """Gerencia temas da aplicação com persistência."""

    _instance: "ThemeManager | None" = None
    _current_theme: Theme = Theme.DARK
    _callbacks: list = []

    # Caminho para arquivo de configuração (mesma pasta do projeto)
    SETTINGS_FILE: Final[Path] = Path.home() / ".config" / "memap" / "theme.json"

    def __new__(cls) -> "ThemeManager":
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Inicializa o gerenciador de temas."""
        if not hasattr(self, '_initialized'):
            self._initialized = True
            try:
                self._load_saved_theme()
            except Exception as e:
                print(f"Aviso: Erro ao inicializar tema, usando padrão: {e}")
                self._current_theme = Theme.DARK

    @property
    def current_theme(self) -> Theme:
        """Retorna o tema atual."""
        return self._current_theme

    @property
    def current_palette(self) -> ColorPalette:
        """Retorna a paleta de cores do tema atual."""
        return DARK_THEME if self._current_theme == Theme.DARK else LIGHT_THEME

    def set_theme(self, theme: Theme) -> None:
        """Define o tema atual e notifica callbacks.

        Args:
            theme: Tema a ser aplicado
        """
        if self._current_theme != theme:
            self._current_theme = theme
            self._save_theme()
            self._notify_callbacks()

    def toggle_theme(self) -> Theme:
        """Alterna entre dark e light theme.

        Returns:
            Novo tema aplicado
        """
        new_theme = Theme.LIGHT if self._current_theme == Theme.DARK else Theme.DARK
        self.set_theme(new_theme)
        return new_theme

    def register_callback(self, callback: callable) -> None:
        """Registra callback a ser chamado quando tema mudar.

        Args:
            callback: Função a ser chamada (sem parâmetros)
        """
        if callback not in self._callbacks:
            self._callbacks.append(callback)

    def unregister_callback(self, callback: callable) -> None:
        """Remove callback registrado.

        Args:
            callback: Função a ser removida
        """
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def _notify_callbacks(self) -> None:
        """Notifica todos os callbacks registrados."""
        for callback in self._callbacks:
            try:
                callback()
            except Exception as e:
                print(f"Erro ao executar callback de tema: {e}")

    def _save_theme(self) -> None:
        """Salva tema atual em arquivo."""
        try:
            # Cria diretório se não existir
            settings_dir = self.SETTINGS_FILE.parent
            if not settings_dir.exists():
                settings_dir.mkdir(parents=True, exist_ok=True)

            # Salva tema
            with open(self.SETTINGS_FILE, 'w', encoding='utf-8') as f:
                json.dump({"theme": self._current_theme.value}, f, indent=2)
        except (OSError, IOError, PermissionError) as e:
            # Silencia erros de I/O - não são críticos
            pass
        except Exception as e:
            # Log outros erros mas não propaga
            print(f"Aviso: Não foi possível salvar preferência de tema: {e}")

    def _load_saved_theme(self) -> None:
        """Carrega tema salvo do arquivo."""
        try:
            if self.SETTINGS_FILE.exists():
                with open(self.SETTINGS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    theme_value = data.get("theme", "dark")
                    # Valida que o tema existe
                    if theme_value in ("dark", "light"):
                        self._current_theme = Theme(theme_value)
                    else:
                        self._current_theme = Theme.DARK
            else:
                # Arquivo não existe - usa padrão
                self._current_theme = Theme.DARK
        except (OSError, IOError, json.JSONDecodeError) as e:
            # Erro ao ler - usa tema padrão
            self._current_theme = Theme.DARK
        except Exception as e:
            # Qualquer outro erro - usa tema padrão
            print(f"Aviso: Não foi possível carregar preferência de tema: {e}")
            self._current_theme = Theme.DARK

    def get_stylesheet(self, component: str) -> str:
        """Gera stylesheet para um componente baseado no tema atual.

        Args:
            component: Nome do componente

        Returns:
            String com CSS do componente
        """
        palette = self.current_palette

        stylesheets = {
            "main": f"""
                QMainWindow {{
                    background-color: {palette.background};
                    color: {palette.text_primary};
                }}
            """,
            "sidebar": f"""
                QFrame#sidebar {{
                    background-color: {palette.background_secondary};
                    border-right: 1px solid {palette.border};
                }}
            """,
            "button": f"""
                QPushButton {{
                    background-color: {palette.primary};
                    color: #FFFFFF;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }}
                QPushButton:hover {{
                    background-color: {palette.primary_hover};
                }}
                QPushButton:pressed {{
                    background-color: {palette.primary_pressed};
                }}
                QPushButton:disabled {{
                    background-color: {palette.background_tertiary};
                    color: {palette.text_disabled};
                }}
            """,
            "table": f"""
                QTableWidget {{
                    background-color: {palette.background};
                    color: {palette.text_primary};
                    gridline-color: {palette.border};
                    border: 1px solid {palette.border};
                    border-radius: 4px;
                }}
                QTableWidget::item {{
                    padding: 5px;
                }}
                QTableWidget::item:selected {{
                    background-color: {palette.selection};
                }}
                QHeaderView::section {{
                    background-color: {palette.background_tertiary};
                    color: {palette.text_primary};
                    padding: 5px;
                    border: 1px solid {palette.border};
                    font-weight: bold;
                }}
            """
        }

        return stylesheets.get(component, "")
