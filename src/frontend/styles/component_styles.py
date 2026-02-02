"""
Estilos de componentes específicos para a aplicação MeMap Pro.
Separa os estilos inline em classes reutilizáveis.
"""

from src.frontend.styles.styles import ColorPalette


class SidebarStyles:
    """Estilos para componentes do Sidebar."""

    colors = ColorPalette()

    @staticmethod
    def get_title_style() -> str:
        """Retorna o estilo para o título do sidebar."""
        return f"""
            QLabel#sidebar_title {{
                font-size: 18px;
                font-weight: 700;
                color: {SidebarStyles.colors.ACCENT};
                margin-bottom: 16px;
                border-bottom: 1px solid #333;
                padding-bottom: 8px;
            }}
        """


class NavbarStyles:
    """Estilos para componentes da Navbar."""

    colors = ColorPalette()

    @staticmethod
    def get_page_title_style() -> str:
        """Retorna o estilo para o título da página."""
        return f"""
            QLabel#page_title {{
                font-size: 16px;
                font-weight: 600;
                color: {NavbarStyles.colors.TEXT_PRIMARY};
            }}
        """

    @staticmethod
    def get_status_label_style() -> str:
        """Retorna o estilo para o label de status."""
        return f"""
            QLabel#status_label {{
                font-size: 12px;
                color: {NavbarStyles.colors.TEXT_SECONDARY};
                background-color: {NavbarStyles.colors.SURFACE_HOVER};
                border: 1px solid #333;
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """


class FooterStyles:
    """Estilos para componentes do Footer."""

    colors = ColorPalette()

    @staticmethod
    def get_system_info_style() -> str:
        """Retorna o estilo para informações do sistema."""
        return f"""
            QLabel#system_info {{
                font-size: 11px;
                color: {FooterStyles.colors.TEXT_SECONDARY};
            }}
        """

    @staticmethod
    def get_progress_bar_style() -> str:
        """Retorna o estilo para a barra de progresso."""
        return f"""
            QProgressBar#global_progress {{
                background-color: {FooterStyles.colors.SURFACE_PRESSED};
                border: 1px solid #333;
                border-radius: 6px;
                text-align: center;
                color: transparent;
            }}
            QProgressBar#global_progress::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {FooterStyles.colors.ACCENT},
                    stop:1 {FooterStyles.colors.ACCENT_HOVER});
                border-radius: 5px;
            }}
        """


class DashboardPageStyles:
    """Estilos para componentes da página Dashboard."""

    colors = ColorPalette()

    @staticmethod
    def get_title_style() -> str:
        """Retorna o estilo para o título da página."""
        return f"""
            font-size: 24px;
            font-weight: 700;
            color: {DashboardPageStyles.colors.TEXT_PRIMARY};
        """

    @staticmethod
    def get_description_style() -> str:
        """Retorna o estilo para a descrição."""
        return f"""
            font-size: 14px;
            color: {DashboardPageStyles.colors.TEXT_SECONDARY};
        """

    @staticmethod
    def get_column_title_style() -> str:
        """Retorna o estilo para títulos das colunas."""
        return f"""
            font-size: 14px;
            font-weight: 600;
            color: {DashboardPageStyles.colors.ACCENT};
        """

    @staticmethod
    def get_column_content_style() -> str:
        """Retorna o estilo para conteúdo das colunas."""
        return f"""
            font-size: 12px;
            color: {DashboardPageStyles.colors.TEXT_SECONDARY};
            text-align: center;
        """


class TaskWidgetStyles:
    """Estilos para widgets de tarefas."""

    colors = ColorPalette()

    @staticmethod
    def get_task_frame_style() -> str:
        """Retorna o estilo para o frame da tarefa."""
        return f"""
            QFrame {{
                background-color: {TaskWidgetStyles.colors.SURFACE_HOVER};
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
            }}
        """

    @staticmethod
    def get_checkbox_style() -> str:
        """Retorna o estilo para o checkbox."""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                font-size: 16px;
                color: {TaskWidgetStyles.colors.TEXT_SECONDARY};
            }}
            QPushButton:hover {{
                color: {TaskWidgetStyles.colors.ACCENT};
            }}
        """

    @staticmethod
    def get_task_name_style() -> str:
        """Retorna o estilo para o nome da tarefa."""
        return f"""
            font-size: 14px;
            font-weight: 600;
            color: {TaskWidgetStyles.colors.TEXT_PRIMARY};
        """

    @staticmethod
    def get_task_details_style() -> str:
        """Retorna o estilo para detalhes da tarefa."""
        return f"""
            font-size: 12px;
            color: {TaskWidgetStyles.colors.TEXT_SECONDARY};
        """


class ChartWidgetStyles:
    """Estilos para widgets de gráficos."""

    colors = ColorPalette()

    @staticmethod
    def get_chart_frame_style() -> str:
        """Retorna o estilo para o frame do gráfico."""
        return f"""
            QFrame {{
                background-color: {ChartWidgetStyles.colors.SURFACE_HOVER};
                border: 1px solid #333;
                border-radius: 8px;
                padding: 16px;
            }}
        """

    @staticmethod
    def get_chart_title_style() -> str:
        """Retorna o estilo para o título do gráfico."""
        return f"""
            font-size: 14px;
            font-weight: 600;
            color: {ChartWidgetStyles.colors.TEXT_PRIMARY};
        """

    @staticmethod
    def get_chart_area_style() -> str:
        """Retorna o estilo para a área do gráfico."""
        return f"""
            font-size: 12px;
            color: {ChartWidgetStyles.colors.TEXT_SECONDARY};
            background-color: {ChartWidgetStyles.colors.SURFACE_PRESSED};
            border-radius: 4px;
            padding: 20px;
        """


class SettingsPageStyles:
    """Estilos para componentes da página de Configurações."""

    colors = ColorPalette()

    @staticmethod
    def get_title_style() -> str:
        """Retorna o estilo para o título."""
        return f"""
            font-size: 24px;
            font-weight: 700;
            color: {SettingsPageStyles.colors.TEXT_PRIMARY};
        """

    @staticmethod
    def get_description_style() -> str:
        """Retorna o estilo para a descrição."""
        return f"""
            font-size: 14px;
            color: {SettingsPageStyles.colors.TEXT_SECONDARY};
        """

    @staticmethod
    def get_section_label_style() -> str:
        """Retorna o estilo para labels de seção."""
        return f"""
            font-weight: 600;
            color: {SettingsPageStyles.colors.TEXT_PRIMARY};
        """


class CalendarWidgetStyles:
    """Estilos para widgets de calendário."""

    colors = ColorPalette()

    @staticmethod
    def get_calendar_style() -> str:
        """Retorna o estilo completo para o calendário."""
        return f"""
            QCalendarWidget QWidget {{
                color: {CalendarWidgetStyles.colors.TEXT_PRIMARY};
                background-color: {CalendarWidgetStyles.colors.SURFACE_HOVER};
            }}
            QCalendarWidget QTableView {{
                border: 1px solid #333;
                border-radius: 8px;
            }}
            QCalendarWidget QTableView QTableCornerButton::section {{
                background-color: {CalendarWidgetStyles.colors.SURFACE_HOVER};
                border: 1px solid #333;
            }}
            QCalendarWidget QTableView QHeaderView::section {{
                background-color: {CalendarWidgetStyles.colors.SURFACE_HOVER};
                color: {CalendarWidgetStyles.colors.TEXT_PRIMARY};
                border: 1px solid #333;
                font-weight: bold;
                padding: 8px;
                min-height: 36px;
            }}
            QCalendarWidget QTableView::item {{
                border: 1px solid #333;
                padding: 12px;
                min-height: 100px;
                min-width: 100px;
            }}
            QCalendarWidget QTableView::item:selected {{
                background-color: {CalendarWidgetStyles.colors.ACCENT};
                color: white;
                border: 2px solid {CalendarWidgetStyles.colors.ACCENT_HOVER};
            }}
            QCalendarWidget QTableView::item:hover {{
                background-color: {CalendarWidgetStyles.colors.SURFACE_PRESSED};
                border: 1px solid {CalendarWidgetStyles.colors.ACCENT};
            }}
            QCalendarWidget QToolButton {{
                color: {CalendarWidgetStyles.colors.TEXT_PRIMARY};
                background-color: {CalendarWidgetStyles.colors.SURFACE_HOVER};
                border: 1px solid #333;
                border-radius: 6px;
                min-height: 36px;
                padding: 8px 16px;
            }}
            QCalendarWidget QToolButton:hover {{
                background-color: {CalendarWidgetStyles.colors.SURFACE_PRESSED};
            }}
            QCalendarWidget QSpinBox {{
                color: {CalendarWidgetStyles.colors.TEXT_PRIMARY};
                background-color: {CalendarWidgetStyles.colors.SURFACE_HOVER};
                border: 1px solid #333;
                border-radius: 6px;
                min-height: 36px;
            }}
            QCalendarWidget QSpinBox::up-button, QCalendarWidget QSpinBox::down-button {{
                width: 24px;
                height: 24px;
            }}
        """
