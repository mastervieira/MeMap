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
        self.colors = ColorPalette()

    def get_main_stylesheet(self) -> str:
        """Retorna o stylesheet principal da aplicação."""
        return f"""
        /* Estilo Global */
        QMainWindow {{
            background-color: {self.colors.BACKGROUND};
            color: {self.colors.TEXT_PRIMARY};
        }}

        QWidget {{
            font-family: 'Segoe UI', 'Inter', Arial, sans-serif;
            font-size: 14px;
            color: {self.colors.TEXT_PRIMARY};
        }}

        /* Botões Primários */
        QPushButton {{
            background-color: {self.colors.PRIMARY};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            min-height: 36px;
        }}

        QPushButton:hover {{
            background-color: {self.colors.PRIMARY_HOVER};
        }}

        QPushButton:pressed {{
            background-color: {self.colors.PRIMARY_PRESSED};
        }}

        QPushButton:disabled {{
            background-color: {self.colors.TEXT_DISABLED};
            color: {self.colors.TEXT_SECONDARY};
        }}

        /* Botões Secundários */
        QPushButton[secondary="true"] {{
            background-color: transparent;
            color: {self.colors.TEXT_PRIMARY};
            border: 1px solid {self.colors.SECONDARY};
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            min-height: 36px;
        }}

        QPushButton[secondary="true"]:hover {{
            background-color: {self.colors.SECONDARY_HOVER};
            border-color: {self.colors.SECONDARY_HOVER};
        }}

        QPushButton[secondary="true"]:pressed {{
            background-color: {self.colors.SECONDARY_PRESSED};
            border-color: {self.colors.SECONDARY_PRESSED};
        }}

        /* Botões de Erro */
        QPushButton[error="true"] {{
            background-color: {self.colors.ERROR};
            color: white;
            border: none;
            border-radius: 8px;
            padding: 10px 16px;
            font-weight: 600;
            min-height: 36px;
        }}

        QPushButton[error="true"]:hover {{
            background-color: {self.colors.ERROR_HOVER};
        }}

        QPushButton[error="true"]:pressed {{
            background-color: {self.colors.ERROR_PRESSED};
        }}

        /* Sidebar */
        QFrame#sidebar {{
            background-color: {self.colors.SURFACE};
            border-right: 1px solid #333;
            min-width: 240px;
            max-width: 240px;
        }}

        /* Navbar */
        QFrame#navbar {{
            background-color: {self.colors.SURFACE};
            border-bottom: 1px solid #333;
            min-height: 60px;
        }}

        /* Footer */
        QFrame#footer {{
            background-color: {self.colors.SURFACE};
            border-top: 1px solid #333;
            min-height: 40px;
        }}

        /* Conteúdo Principal */
        QFrame#main_content {{
            background-color: {self.colors.BACKGROUND};
        }}

        /* Tabelas */
        QTableWidget {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 8px;
            gridline-color: #333;
            selection-background-color: {self.colors.ACCENT};
            selection-color: white;
        }}

        QTableWidget QHeaderView::section {{
            background-color: {self.colors.SURFACE_HOVER};
            color: {self.colors.TEXT_PRIMARY};
            border: none;
            padding: 8px;
            font-weight: 600;
        }}

        /* Progress Bar */
        QProgressBar {{
            border: 1px solid #333;
            border-radius: 4px;
            text-align: center;
            background-color: {self.colors.SURFACE};
        }}

        QProgressBar::chunk {{
            background-color: {self.colors.ACCENT};
            width: 20px;
        }}

        /* Labels */
        QLabel {{
            color: {self.colors.TEXT_PRIMARY};
        }}

        QLabel[secondary="true"] {{
            color: {self.colors.TEXT_SECONDARY};
            font-size: 12px;
        }}

        /* Line Edit */
        QLineEdit {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 6px;
            padding: 8px 12px;
            color: {self.colors.TEXT_PRIMARY};
        }}

        QLineEdit:focus {{
            border-color: {self.colors.ACCENT};
            background-color: {self.colors.SURFACE_HOVER};
        }}

        /* Combobox */
        QComboBox {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 6px;
            padding: 8px 12px;
            color: {self.colors.TEXT_PRIMARY};
            min-height: 36px;
        }}

        QComboBox::drop-down {{
            border: none;
        }}

        QComboBox QAbstractItemView {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            selection-background-color: {self.colors.ACCENT};
        }}

        /* Scrollbar */
        QScrollBar:vertical {{
            background: {self.colors.SURFACE};
            width: 16px;
            border-left: 1px solid #333;
        }}

        QScrollBar::handle:vertical {{
            background: {self.colors.SECONDARY};
            min-height: 20px;
            border-radius: 8px;
            margin: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: {self.colors.SECONDARY_HOVER};
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            background: none;
        }}

        /* Mensagens de Status */
        QLabel#status_message {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 6px;
            padding: 8px 12px;
            color: {self.colors.TEXT_PRIMARY};
        }}

        QLabel#status_error {{
            background-color: {self.colors.ERROR};
            color: white;
            border-radius: 6px;
            padding: 8px 12px;
        }}

        QLabel#status_success {{
            background-color: {self.colors.SUCCESS};
            color: white;
            border-radius: 6px;
            padding: 8px 12px;
        }}

        /* Calendário */
        QCalendarWidget QWidget {{
            color: {self.colors.TEXT_PRIMARY};
            background-color: {self.colors.SURFACE};
        }}

        QCalendarWidget QTableView {{
            border: 1px solid #333;
            border-radius: 8px;
        }}

        QCalendarWidget QTableView QTableCornerButton::section {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
        }}

        QCalendarWidget QTableView QHeaderView::section {{
            background-color: {self.colors.SURFACE_HOVER};
            color: {self.colors.TEXT_PRIMARY};
            border: 1px solid #333;
            font-weight: bold;
            padding: 8px;
            min-height: 36px;
            font-size: 14px;
        }}

        QCalendarWidget QTableView::item {{
            border: 1px solid #333;
            padding: 12px;
            min-height: 100px;
            min-width: 100px;
        }}

        QCalendarWidget QTableView::item:selected {{
            background-color: {self.colors.ACCENT};
            color: white;
            border: 2px solid {self.colors.ACCENT_HOVER};
        }}

        QCalendarWidget QTableView::item:hover {{
            background-color: {self.colors.SURFACE_HOVER};
            border: 1px solid {self.colors.ACCENT};
        }}

        QCalendarWidget QToolButton {{
            color: {self.colors.TEXT_PRIMARY};
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 6px;
            min-height: 36px;
            padding: 8px 16px;
            font-size: 16px;
            font-weight: bold;
        }}

        QCalendarWidget QToolButton:hover {{
            background-color: {self.colors.SURFACE_HOVER};
        }}

        QCalendarWidget QSpinBox {{
            color: {self.colors.TEXT_PRIMARY};
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
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
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 12px;
            padding: 16px;
        }}

        QFrame#lower_grid {{
            background-color: {self.colors.SURFACE};
            border: 1px solid #333;
            border-radius: 12px;
            padding: 15px;
        }}

        QFrame#column_1 {{
            background-color: {self.colors.SURFACE_HOVER};
            border: 1px solid #333;
            border-radius: 8px;
            padding: 12px;
            margin-right: 8px;
        }}

        QFrame#columns_23 {{
            background-color: {self.colors.SURFACE_HOVER};
            border: 1px solid #333;
            border-radius: 8px;
        }}

        QFrame#column_2 {{
            background-color: {self.colors.SURFACE_HOVER};
            border: none;
            padding: 12px;
        }}

        QFrame#column_3 {{
            background-color: {self.colors.SURFACE_HOVER};
            border: none;
            padding: 12px;
        }}

        QFrame#divider_23 {{
            background: qlineargradient(
                x1:0, y1:0, x2:0, y2:1,
                stop:0 #333,
                stop:0.5 {self.colors.ACCENT},
                stop:1 #333
            );
            border: none;
        }}
        """

    def get_sidebar_button_style(self, is_active: bool = False) -> str:
        """Retorna o estilo para botões do sidebar."""
        if is_active:
            return f"""
            QPushButton {{
                background-color: {self.colors.ACCENT};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-weight: 600;
                min-height: 44px;
            }}

            QPushButton:hover {{
                background-color: {self.colors.ACCENT_HOVER};
            }}
            """
        else:
            return f"""
            QPushButton {{
                background-color: transparent;
                color: {self.colors.TEXT_PRIMARY};
                border: none;
                border-radius: 8px;
                padding: 12px 16px;
                text-align: left;
                font-weight: 500;
                min-height: 44px;
            }}

            QPushButton:hover {{
                background-color: {self.colors.SURFACE_HOVER};
                color: {self.colors.TEXT_PRIMARY};
            }}

            QPushButton:pressed {{
                background-color: {self.colors.SURFACE_PRESSED};
            }}
            """
