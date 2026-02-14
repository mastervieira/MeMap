"""
Estilos de componentes específicos para a aplicação MeMap Pro.
Separa os estilos inline em classes reutilizáveis.
"""

from src.common.themes.colors import ColorPalette
from src.common.themes import ThemeManager


class SidebarStyles:
    """Estilos para componentes do Sidebar."""

    @staticmethod
    def get_title_style() -> str:
        """Retorna o estilo para o título do sidebar."""
        palette = ThemeManager().current_palette
        return f"""
            QLabel#sidebar_title {{
                font-size: 18px;
                font-weight: 700;
                color: {palette.accent};
                margin-bottom: 16px;
                border-bottom: 1px solid {palette.border};
                padding-bottom: 8px;
            }}
        """


class NavbarStyles:
    """Estilos para componentes da Navbar."""

    @staticmethod
    def get_page_title_style() -> str:
        """Retorna o estilo para o título da página."""
        palette = ThemeManager().current_palette
        return f"""
            QLabel#page_title {{
                font-size: 16px;
                font-weight: 600;
                color: {palette.text_primary};
            }}
        """

    @staticmethod
    def get_status_label_style() -> str:
        """Retorna o estilo para o label de status."""
        palette = ThemeManager().current_palette
        return f"""
            QLabel#status_label {{
                font-size: 12px;
                color: {palette.text_secondary};
                background-color: {palette.surface_hover};
                border: 1px solid {palette.border};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """


class FooterStyles:
    """Estilos para componentes do Footer."""

    @staticmethod
    def get_system_info_style() -> str:
        """Retorna o estilo para informações do sistema."""
        palette = ThemeManager().current_palette
        return f"""
            QLabel#system_info {{
                font-size: 11px;
                color: {palette.text_secondary};
            }}
        """

    @staticmethod
    def get_progress_bar_style() -> str:
        """Retorna o estilo para a barra de progresso."""
        palette = ThemeManager().current_palette
        return f"""
            QProgressBar#global_progress {{
                background-color: {palette.background_tertiary};
                border: 1px solid {palette.border};
                border-radius: 6px;
                text-align: center;
                color: transparent;
            }}
            QProgressBar#global_progress::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {palette.accent},
                    stop:1 {palette.accent_hover});
                border-radius: 5px;
            }}
        """


class DashboardPageStyles:
    """Estilos para componentes da página Dashboard."""

    @staticmethod
    def get_title_style() -> str:
        """Retorna o estilo para o título da página."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 24px;
            font-weight: 700;
            color: {palette.text_primary};
        """

    @staticmethod
    def get_description_style() -> str:
        """Retorna o estilo para a descrição."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 14px;
            color: {palette.text_secondary};
        """

    @staticmethod
    def get_column_title_style() -> str:
        """Retorna o estilo para títulos das colunas."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 14px;
            font-weight: 600;
            color: {palette.accent};
        """

    @staticmethod
    def get_column_content_style() -> str:
        """Retorna o estilo para conteúdo das colunas."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 12px;
            color: {palette.text_secondary};
            text-align: center;
        """


class TaskWidgetStyles:
    """Estilos para widgets de tarefas."""

    @staticmethod
    def get_task_frame_style() -> str:
        """Retorna o estilo para o frame da tarefa."""
        palette = ThemeManager().current_palette
        return f"""
            QFrame {{
                background-color: {palette.surface_hover};
                border: 1px solid {palette.border};
                border-radius: 8px;
                padding: 12px;
            }}
        """

    @staticmethod
    def get_checkbox_style() -> str:
        """Retorna o estilo para o checkbox."""
        palette = ThemeManager().current_palette
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: {palette.text_secondary};
            }}
            QPushButton:hover {{
                color: {palette.accent};
            }}
        """

    @staticmethod
    def get_task_name_style() -> str:
        """Retorna o estilo para o nome da tarefa."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 14px;
            font-weight: 600;
            color: {palette.text_primary};
        """

    @staticmethod
    def get_task_details_style() -> str:
        """Retorna o estilo para detalhes da tarefa."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 12px;
            color: {palette.text_secondary};
        """


class ChartWidgetStyles:
    """Estilos para widgets de gráficos."""

    @staticmethod
    def get_chart_frame_style() -> str:
        """Retorna o estilo para o frame do gráfico."""
        palette = ThemeManager().current_palette
        return f"""
            QFrame {{
                background-color: {palette.surface_hover};
                border: 1px solid {palette.border};
                border-radius: 8px;
                padding: 16px;
            }}
        """

    @staticmethod
    def get_chart_title_style() -> str:
        """Retorna o estilo para o título do gráfico."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 14px;
            font-weight: 600;
            color: {palette.text_primary};
        """

    @staticmethod
    def get_chart_area_style() -> str:
        """Retorna o estilo para a área do gráfico."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 12px;
            color: {palette.text_secondary};
            background-color: {palette.background_tertiary};
            border-radius: 4px;
            padding: 20px;
        """


class SettingsPageStyles:
    """Estilos para componentes da página de Configurações."""

    @staticmethod
    def get_title_style() -> str:
        """Retorna o estilo para o título."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 24px;
            font-weight: 700;
            color: {palette.text_primary};
        """

    @staticmethod
    def get_description_style() -> str:
        """Retorna o estilo para a descrição."""
        palette = ThemeManager().current_palette
        return f"""
            font-size: 14px;
            color: {palette.text_secondary};
        """

    @staticmethod
    def get_section_label_style() -> str:
        """Retorna o estilo para labels de seção."""
        palette = ThemeManager().current_palette
        return f"""
            font-weight: 600;
            color: {palette.text_primary};
        """


class CalendarWidgetStyles:
    """Estilos para widgets de calendário."""

    @staticmethod
    def get_calendar_style() -> str:
        """Retorna o estilo completo para o calendário."""
        palette: ColorPalette = ThemeManager().current_palette
        return f"""
            QCalendarWidget QWidget {{
                color: {palette.text_primary};
                background-color: {palette.background_secondary};
            }}
            QCalendarWidget QTableView {{
                border: none;
                background-color: {palette.background_secondary};
            }}
            QCalendarWidget QTableView QTableCornerButton::section {{
                background-color: {palette.background_secondary};
                border: none;
            }}
            QCalendarWidget QTableView QHeaderView::section {{
                background-color: {palette.background_secondary};
                color: {palette.text_primary};
                border: none;
                border-bottom: 1px solid {palette.border};
                font-weight: bold;
                padding: 8px;
                min-height: 36px;
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
                border: 1px solid {palette.accent_hover};
            }}
            QCalendarWidget QTableView::item:hover {{
                background-color: {palette.surface_hover};
                border: 1px solid {palette.accent};
            }}
            QCalendarWidget QToolButton {{
                color: {palette.text_primary};
                background-color: {palette.background_secondary};
                border: none;
                border-radius: 6px;
                min-height: 36px;
                padding: 8px 16px;
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
            }}
            QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {{
                width: 24px;
                height: 24px;
            }}
        """
