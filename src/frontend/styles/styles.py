"""
Estilos QSS avançados para aplicação PySide6 com design Flat UI Dark Mode.
Inspiração: VS Code e Spotify.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor


class ColorPalette:
    """Dicionário de cores para o design Dark Mode."""

    # Cores Primárias
    PRIMARY = "#007ACC"  # Azul VS Code
    PRIMARY_HOVER = "#005A9E"
    PRIMARY_PRESSED = "#004477"

    # Cores Secundárias
    SECONDARY = "#5F6368"  # Cinza claro
    SECONDARY_HOVER = "#7A7F85"
    SECONDARY_PRESSED = "#4A4F54"

    # Cores de Fundo
    BACKGROUND = "#1E1E1E"  # Fundo principal (VS Code)
    SURFACE = "#252526"     # Superfícies (painéis)
    SURFACE_HOVER = "#2D2D30"
    SURFACE_PRESSED = "#37373D"

    # Cores de Texto
    TEXT_PRIMARY = "#D4D4D4"  # Texto principal
    TEXT_SECONDARY = "#A0A0A0"  # Texto secundário
    TEXT_DISABLED = "#6A6A6A"

    # Cores de Erro
    ERROR = "#F44747"
    ERROR_HOVER = "#D13B3B"
    ERROR_PRESSED = "#A82E2E"

    # Cores de Sucesso
    SUCCESS = "#4EC9B0"
    SUCCESS_HOVER = "#3EA090"
    SUCCESS_PRESSED = "#2E7A6E"

    # Cores de Aviso
    WARNING = "#FFCC02"
    WARNING_HOVER = "#E6B800"
    WARNING_PRESSED = "#CC9900"

    # Cores de Destaque
    ACCENT = "#569CD6"  # Azul destaque
    ACCENT_HOVER = "#4AA3D0"
    ACCENT_PRESSED = "#3E86B3"


class StyleManager:
    """Gerenciador de estilos QSS."""

    def __init__(self):
        # Importa aqui para evitar import circular
        from src.common.themes import ThemeManager
        self.theme_manager = ThemeManager()
        # Mantém ColorPalette para compatibilidade, mas não usa
        self.colors = ColorPalette()

    def get_main_stylesheet(self) -> str:
        """Retorna o stylesheet principal da aplicação."""
        # Usa as cores do tema atual (dinâmicas)
        palette = self.theme_manager.current_palette

        return f"""
        /* Estilo Global */
        QMainWindow {{
            background-color: {palette.background};
            color: {palette.text_primary};
        }}

        QWidget {{
            font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            font-size: 14px;
            color: {palette.text_primary};
        }}

        /* Botões Primários */
        QPushButton {{
            background-color: {palette.primary};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            min-height: 36px;
        }}

        QPushButton:hover {{
            background-color: {palette.primary_hover};
        }}

        QPushButton:pressed {{
            background-color: {palette.primary_pressed};
        }}

        QPushButton:disabled {{
            background-color: {palette.text_disabled};
            color: {palette.text_secondary};
        }}

        /* Botões Secundários */
        QPushButton[secondary="true"] {{
            background-color: transparent;
            color: {palette.text_primary};
            border: 1px solid {palette.secondary};
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            min-height: 36px;
        }}

        QPushButton[secondary="true"]:hover {{
            background-color: {palette.secondary_hover};
            border-color: {palette.secondary_hover};
        }}

        QPushButton[secondary="true"]:pressed {{
            background-color: {palette.secondary_pressed};
            border-color: {palette.secondary_pressed};
        }}

        /* Botões de Erro */
        QPushButton[error="true"] {{
            background-color: {palette.error};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            min-height: 36px;
        }}

        QPushButton[error="true"]:hover {{
            background-color: {palette.error_hover};
        }}

        QPushButton[error="true"]:pressed {{
            background-color: {palette.error_pressed};
        }}

        /* Sidebar */
        QFrame#sidebar {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            min-width: 240px;
            max-width: 240px;
        }}

        /* Navbar */
        QFrame#navbar {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            min-height: 60px;
        }}

        /* Footer */
        QFrame#footer {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            min-height: 40px;
        }}

        /* Conteúdo Principal */
        QFrame#main_content {{
            background-color: {palette.background};
        }}

        /* Tabelas */
        QTableWidget {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 8px;
            gridline-color: {palette.border};
            selection-background-color: {palette.accent};
            selection-color: white;
        }}

        QTableWidget QHeaderView::section {{
            background-color: {palette.surface_hover};
            color: {palette.text_primary};
            border: none;
            padding: 8px;
            font-weight: 600;
        }}

        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {palette.border};
            border-radius: 4px;
            text-align: center;
            background-color: {palette.background_secondary};
        }}

        QProgressBar::chunk {{
            background-color: {palette.accent};
            width: 20px;
        }}

        /* Labels */
        QLabel {{
            color: {palette.text_primary};
        }}

        QLabel[secondary="true"] {{
            color: {palette.text_secondary};
            font-size: 12px;
        }}

        /* Line Edit */
        QLineEdit {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 6px;
            padding: 8px 12px;
            color: {palette.text_primary};
        }}

        QLineEdit:focus {{
            border-color: {palette.accent};
            background-color: {palette.surface_hover};
        }}

        /* Combobox */
        QComboBox {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 6px;
            padding: 8px 12px;
            color: {palette.text_primary};
            min-height: 36px;
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox QAbstractItemView {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            selection-background-color: {palette.accent};
        }}

        /* Scrollbar */
        QScrollBar:vertical {{
            background: {palette.background_secondary};
            width: 16px;
            border: 1px solid {palette.border};
        }}

        QScrollBar::handle:vertical {{
            background: {palette.secondary};
            min-height: 20px;
            border-radius: 8px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {palette.secondary_hover};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
        }}

        /* Mensagens de Status */
        QLabel#status_message {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 6px;
            padding: 8px 12px;
            color: {palette.text_primary};
        }}

        QLabel#status_error {{
            background-color: {palette.error};
            color: white;
            border-radius: 6px;
            padding: 8px 12px;
        }}

        QLabel#status_success {{
            background-color: {palette.success};
            color: white;
            border-radius: 6px;
            padding: 8px 12px;
        }}

        /* Calendário */
        QCalendarWidget QWidget {{
            color: {palette.text_primary};
            background-color: {palette.background_secondary};
        }}

        QCalendarWidget QTableView {{
            border: 1px solid {palette.border};
            border-radius: 8px;
        }}

        QCalendarWidget QTableView QTableCornerButton::section {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
        }}

        QCalendarWidget QTableView QHeaderView::section {{
            background-color: {palette.surface_hover};
            color: {palette.text_primary};
            border: 1px solid {palette.border};
            font-weight: bold;
            padding: 8px;
            min-height: 36px;
            font-size: 14px;
        }}

        QCalendarWidget QTableView::item {{
            border: 1px solid {palette.border};
            padding: 12px;
            min-height: 100px;
            min-width: 100px;
        }}

        QCalendarWidget QTableView::item:selected {{
            background-color: {palette.accent};
            color: white;
            border: 2px solid {palette.accent_hover};
        }}

        QCalendarWidget QTableView::item:hover {{
            background-color: {palette.surface_hover};
            border: 1px solid {palette.accent};
        }}

        QCalendarWidget QToolButton {{
            color: {palette.text_primary};
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 6px;
            min-height: 36px;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: bold;
        }}

        QCalendarWidget QToolButton:hover {{
            background-color: {palette.surface_hover};
        }}

        QCalendarWidget QSpinBox {{
            color: {palette.text_primary};
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 6px;
            min-height: 36px;
            font-size: 16px;
            font-weight: bold;
        }}

        QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {{
            width: 24px;
            height: 24px;
        }}

        /* Grids */
        QFrame#upper_grid {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 12px;
            padding: 16px;
        }}

        QFrame#lower_grid {{
            background-color: {palette.background_secondary};
            border: 1px solid {palette.border};
            border-radius: 12px;
            padding: 15px;
        }}

        QFrame#column_1 {{
            background-color: {palette.surface_hover};
            border: 1px solid {palette.border};
            border-radius: 8px;
            padding: 12px;
            margin-right: 8px;
        }}

        QFrame#columns_23 {{
            background-color: {palette.surface_hover};
            border: 1px solid {palette.border};
            border-radius: 8px;
        }}

        QFrame#column_2 {{
            background-color: {palette.surface_hover};
            border: none;
            padding: 12px;
        }}

        QFrame#column_3 {{
            background-color: {palette.surface_hover};
            border: none;
            padding: 12px;
        }}

        QFrame#divider_23 {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #333,
                stop:0.5 {palette.accent},
                stop:1 #333
            );
            border: none;
        }}
        """

    def get_sidebar_button_style(self, is_active: bool = False) -> str:
        """Retorna o estilo para botões do sidebar."""
        # Usa as cores do tema atual
        palette = self.theme_manager.current_palette

        if is_active:
            return f"""
            QPushButton {{
                background-color: {palette.accent};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                min-height: 44px;
            }}

            QPushButton:hover {{
                background-color: {palette.accent_hover};
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: transparent;
                color: {palette.text_primary};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-weight: 500;
                min-height: 44px;
            }}

            QPushButton:hover {{
                background-color: {palette.surface_hover};
                color: {palette.text_primary};
            }}

            QPushButton:pressed {{
                background-color: {palette.background_tertiary};
            }}
            """
