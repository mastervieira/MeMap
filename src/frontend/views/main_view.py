"""
Main View da aplicação com sidebar, navbar e footer.
Implementa a arquitetura principal da interface com nova estrutura de grids.
"""

from PySide6.QtCore import  QSize, Signal, Slot
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from common.themes.colors import ColorPalette
from src.common.themes import Theme, ThemeManager
from src.frontend.styles.styles import StyleManager
from src.frontend.styles.component_styles import (
    SidebarStyles,
    FooterStyles,
    DashboardPageStyles,
)
from src.frontend.views.wizard_view import GuidedFormWizard
from src.frontend.views.calendar_dashboard import CalendarDashboard
from src.frontend.views.controller import CalendarController
from src.common.icons import IconManager
from src.frontend.viewmodels import MainViewModel


class SidebarButton(QPushButton):
    """Botão customizado para o sidebar."""

    def __init__(self, text: str, icon: str = "", parent=None) -> None:
        super().__init__(text, parent)
        self.setProperty("sidebar_button", True)
        # setCursor removido - usa stylesheet para cursor pointer
        self.setMinimumHeight(44)


class Sidebar(QFrame):
    """Sidebar da aplicação com navegação."""

    # Sinais
    page_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setMinimumWidth(240)
        self.setMaximumWidth(300)

        # Inicializa gerenciador de ícones
        self.icon_manager = IconManager()

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(8)

        # Título
        self.title_label = QLabel("MeMap Pro")
        self.title_label.setObjectName("sidebar_title")
        self.title_label.setStyleSheet(SidebarStyles.get_title_style())

        # Botões de navegação com ícones
        self.btn_dashboard = SidebarButton("Dashboard")
        self.btn_dashboard.setIcon(self.icon_manager.dashboard())
        self.btn_dashboard.clicked.connect(
            lambda: self._on_page_changed("dashboard")
        )

        self.btn_wizard = SidebarButton("Novo Formulário")
        self.btn_wizard.setIcon(self.icon_manager.wizard())
        self.btn_wizard.clicked.connect(
            lambda: self._on_page_changed("wizard")
        )

        self.btn_calendar = SidebarButton("Calendário")
        self.btn_calendar.setIcon(self.icon_manager.calendar())
        self.btn_calendar.clicked.connect(
            lambda: self._on_page_changed("calendar")
        )

        self.btn_tasks = SidebarButton("Tarefas")
        self.btn_tasks.setIcon(self.icon_manager.tasks())
        self.btn_tasks.clicked.connect(lambda: self._on_page_changed("tasks"))

        self.btn_analytics = SidebarButton("Análises")
        self.btn_analytics.setIcon(self.icon_manager.analytics())
        self.btn_analytics.clicked.connect(
            lambda: self._on_page_changed("analytics")
        )

        self.btn_settings = SidebarButton("Configurações")
        self.btn_settings.setIcon(self.icon_manager.settings())
        self.btn_settings.clicked.connect(
            lambda: self._on_page_changed("settings")
        )

        # Adiciona widgets ao layout
        self.main_layout.addWidget(self.title_label)
        self.main_layout.addWidget(self.btn_dashboard)
        self.main_layout.addWidget(self.btn_wizard)
        self.main_layout.addWidget(self.btn_calendar)
        self.main_layout.addWidget(self.btn_tasks)
        self.main_layout.addWidget(self.btn_analytics)
        self.main_layout.addWidget(self.btn_settings)

        # Espaço flexível no final
        self.main_layout.addStretch()

        # Registra callback para atualizar ícones quando tema mudar
        self.icon_manager.theme_manager.register_callback(self._update_icons)

        # Define Dashboard como página inicial
        self.set_active_page("dashboard")

    def _update_icons(self) -> None:
        """Atualiza os ícones dos botões quando o tema muda."""
        self.btn_dashboard.setIcon(self.icon_manager.dashboard())
        self.btn_wizard.setIcon(self.icon_manager.wizard())
        self.btn_calendar.setIcon(self.icon_manager.calendar())
        self.btn_tasks.setIcon(self.icon_manager.tasks())
        self.btn_analytics.setIcon(self.icon_manager.analytics())
        self.btn_settings.setIcon(self.icon_manager.settings())

    def set_active_page(self, page_name: str):
        """Define a página ativa no sidebar."""
        buttons = {
            "dashboard": self.btn_dashboard,
            "wizard": self.btn_wizard,
            "calendar": self.btn_calendar,
            "tasks": self.btn_tasks,
            "analytics": self.btn_analytics,
            "settings": self.btn_settings,
        }

        for name, button in buttons.items():
            is_active = name == page_name
            button.setProperty("active", is_active)
            button.style().unpolish(button)
            button.style().polish(button)
            button.update()

    def _on_page_changed(self, page_name: str):
        """Callback quando a página é alterada."""
        self.set_active_page(page_name)
        self.page_changed.emit(page_name)


class Navbar(QFrame):
    """Navbar da aplicação."""

    # Sinal emitido quando botão de tema é clicado
    theme_toggle_requested = Signal()

    def __init__(self, theme_manager: ThemeManager, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")
        self._theme_manager = theme_manager
        self.icon_manager = IconManager()

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 8, 16, 8)
        self.main_layout.setSpacing(16)

        # Título da página
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("page_title")
        # Estilo será aplicado por _apply_theme()

        # Espaço flexível
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Botão de toggle de tema com ícone
        self.theme_toggle_btn = QPushButton()
        self.theme_toggle_btn.setObjectName("theme_toggle")
        self.theme_toggle_btn.setFixedSize(40, 32)
        self.theme_toggle_btn.setIconSize(QSize(20, 20))
        # Remove setCursor - causa warning no Qt
        self.theme_toggle_btn.clicked.connect(self._on_theme_toggle)
        self._update_theme_button()

        # Status da aplicação
        self.status_label = QLabel("Pronto")
        self.status_label.setObjectName("status_label")
        # Estilo será aplicado por _apply_theme()

        # Adiciona widgets ao layout
        self.main_layout.addWidget(self.page_title)
        self.main_layout.addWidget(spacer)
        self.main_layout.addWidget(self.theme_toggle_btn)
        self.main_layout.addWidget(self.status_label)

        # Registra callbacks para atualizar quando tema mudar
        self._theme_manager.register_callback(self._apply_theme)
        self._theme_manager.register_callback(self._update_theme_button)
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Aplica o tema atual ao navbar."""
        # Obtém a paleta do tema atual
        palette: ColorPalette = self._theme_manager.current_palette

        # Aplica estilos dinâmicos baseados no tema
        self.page_title.setStyleSheet(f"""
            QLabel#page_title {{
                font-size: 16px;
                font-weight: 600;
                color: {palette.text_primary};
            }}
        """)

        self.status_label.setStyleSheet(f"""
            QLabel#status_label {{
                font-size: 12px;
                color: {palette.text_secondary};
                background-color: {palette.surface_hover};
                border: 1px solid {palette.border};
                border-radius: 4px;
                padding: 4px 8px;
            }}
        """)

    def _on_theme_toggle(self) -> None:
        """Emite sinal solicitando mudança de tema."""
        self.theme_toggle_requested.emit()

    def _update_theme_button(self) -> None:
        """Atualiza o ícone do botão baseado no tema atual."""
        current_theme = self._theme_manager.current_theme
        if current_theme == Theme.DARK:
            # Em dark mode, mostra sol (para mudar para light)
            self.theme_toggle_btn.setIcon(self.icon_manager.sun())
            self.theme_toggle_btn.setToolTip("Mudar para tema claro")
        else:
            # Em light mode, mostra lua (para mudar para dark)
            self.theme_toggle_btn.setIcon(self.icon_manager.moon())
            self.theme_toggle_btn.setToolTip("Mudar para tema escuro")

    def set_page_title(self, title: str):
        """Atualiza o título da página."""
        self.page_title.setText(title)

    def set_status(self, status: str):
        """Atualiza o status da aplicação."""
        self.status_label.setText(status)


class Footer(QFrame):
    """Footer da aplicação."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("footer")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 8, 16, 8)
        self.main_layout.setSpacing(16)

        # Informações do sistema
        self.system_info = QLabel("PySide6 + qasync • 60fps • Dark Mode")
        self.system_info.setObjectName("system_info")
        self.system_info.setStyleSheet(FooterStyles.get_system_info_style())

        # Espaço flexível
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Container de Progresso
        self.progress_widget = QWidget()
        self.progress_layout = QHBoxLayout(self.progress_widget)
        self.progress_layout.setContentsMargins(0, 0, 0, 0)
        self.progress_layout.setSpacing(10)

        self.progress_label = QLabel("A processar...")
        self.progress_label.setStyleSheet("font-size: 11px; color: #888; font-style: italic;")
        self.progress_label.hide()

        # Progresso geral
        self.global_progress = QProgressBar()
        self.global_progress.setObjectName("global_progress")
        self.global_progress.setRange(0, 100)
        self.global_progress.setValue(0)
        self.global_progress.setTextVisible(False)
        self.global_progress.setFixedHeight(8)
        self.global_progress.setMinimumWidth(200)
        self.global_progress.setStyleSheet(FooterStyles.get_progress_bar_style())
        self.global_progress.hide()

        self.progress_layout.addWidget(self.progress_label)
        self.progress_layout.addWidget(self.global_progress)

        # Adiciona widgets ao layout
        self.main_layout.addWidget(self.system_info)
        self.main_layout.addWidget(spacer)
        self.main_layout.addWidget(self.progress_widget)

    def set_progress(self, value: int, message: str = "A carregar..."):
        """Atualiza o progresso global e visibilidade."""
        from PySide6.QtCore import QTimer

        if 0 < value < 100:
            self.progress_label.setText(message)
            self.progress_label.show()
            self.global_progress.show()
            self.global_progress.setValue(value)
        elif value >= 100:
            self.global_progress.setValue(100)
            self.progress_label.setText("Concluído")
            # Esconde após 1.5 segundos para um efeito elegante
            QTimer.singleShot(1500, self._hide_progress)
        else:
            self._hide_progress()

    def _hide_progress(self):
        """Esconde os widgets de progresso."""
        self.progress_label.hide()
        self.global_progress.hide()
        self.global_progress.setValue(0)


class DashboardPage(QWidget):
    """Página de Dashboard com nova estrutura de grids."""

    # Sinal para solicitar mudança de página
    request_page_change = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.register_callback(self._apply_theme)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)

        # Título
        self.title = QLabel("Dashboard Principal")

        # Descrição
        self.description = QLabel(
            "Bem-vindo ao MeMap Pro! Sistema de gerenciamento com interface moderna."
        )

        # Grid Superior
        self.upper_grid = self.create_upper_grid()

        # Grid Inferior - Calendário
        self.lower_grid = self.create_lower_grid()

        # Adiciona widgets ao layout principal
        self.main_layout.addWidget(self.title)
        self.main_layout.addWidget(self.description)
        self.main_layout.addWidget(self.upper_grid)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.lower_grid)

        # Aplica tema inicial
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Aplica o tema atual aos componentes do dashboard."""
        palette = self.theme_manager.current_palette

        # Atualiza título e descrição
        self.title.setStyleSheet(DashboardPageStyles.get_title_style())
        self.description.setStyleSheet(DashboardPageStyles.get_description_style())

        # Verifica se os frames já foram criados
        if not hasattr(self, 'upper_grid_frame'):
            return

        # Atualiza upper_grid
        self.upper_grid_frame.setStyleSheet(f"""
            QFrame#upper_grid {{
                background-color: {palette.background_secondary};
                border: 1px solid {palette.border};
                border-radius: 12px;
                padding: 16px;
            }}
        """)

        # Atualiza column_1
        self.column1_frame.setStyleSheet(f"""
            QFrame#column_1 {{
                background-color: {palette.surface_hover};
                border: 1px solid {palette.border};
                border-radius: 8px;
                padding: 12px;
                margin-right: 8px;
            }}
        """)

        # Atualiza columns_23
        self.columns_23_frame.setStyleSheet(f"""
            QFrame#columns_23 {{
                background-color: {palette.surface_hover};
                border: 1px solid {palette.border};
                border-radius: 8px;
            }}
        """)

        # Atualiza column_2
        self.column2_frame.setStyleSheet(f"""
            QFrame#column_2 {{
                background-color: {palette.surface_hover};
                border: none;
                padding: 12px;
            }}
        """)

        # Atualiza column_3
        self.column3_frame.setStyleSheet(f"""
            QFrame#column_3 {{
                background-color: {palette.surface_hover};
                border: none;
                padding: 12px;
            }}
        """)

        # Atualiza divider
        self.divider.setStyleSheet(f"background: {palette.border};")

        # Atualiza lower_grid
        self.lower_grid_frame.setStyleSheet(f"""
            QFrame#lower_grid {{
                background-color: {palette.background_secondary};
                border: 1px solid {palette.border};
                border-radius: 12px;
                padding: 15px;
            }}
        """)

    def create_upper_grid(self):
        """Cria a grid superior com 3 colunas."""
        self.upper_grid_frame = QFrame()
        self.upper_grid_frame.setObjectName("upper_grid")
        grid_container = self.upper_grid_frame

        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # ===== COLUNA 1: Botões =====
        self.column1_frame = QFrame()
        self.column1_frame.setObjectName("column_1")
        column1_frame = self.column1_frame

        column1_layout = QVBoxLayout(column1_frame)
        column1_layout.setSpacing(8)
        column1_layout.setContentsMargins(0, 0, 0, 0)

        # Botão que abre o formulário guiado
        btn_col1_1 = QPushButton("Formulário")
        btn_col1_1.setProperty("secondary", True)
        btn_col1_1.setMinimumHeight(40)
        btn_col1_1.clicked.connect(lambda: self.request_page_change.emit("wizard"))

        btn_col1_2 = QPushButton("Intelligence")
        btn_col1_2.setProperty("secondary", True)
        btn_col1_2.setMinimumHeight(40)

        btn_col1_3 = QPushButton("Taxas Lookup")
        btn_col1_3.setProperty("secondary", True)
        btn_col1_3.setMinimumHeight(40)

        column1_layout.addWidget(btn_col1_1)
        column1_layout.addWidget(btn_col1_2)
        column1_layout.addWidget(btn_col1_3)
        column1_layout.addStretch()

        grid_layout.addWidget(column1_frame, 0, 0)

        # ===== COLUNAS 2 e 3: Coladas com divisor =====
        self.columns_23_frame = QFrame()
        self.columns_23_frame.setObjectName("columns_23")
        columns_23_frame = self.columns_23_frame

        columns_23_layout = QHBoxLayout(columns_23_frame)
        columns_23_layout.setSpacing(0)
        columns_23_layout.setContentsMargins(0, 0, 0, 0)

        # Coluna 2: Dados
        self.column2_frame = QFrame()
        self.column2_frame.setObjectName("column_2")
        column2_frame = self.column2_frame
        column2_layout = QVBoxLayout(column2_frame)
        column2_layout.addWidget(QLabel("Dados"))
        column2_layout.addStretch()

        # Divisor
        self.divider = QFrame()
        self.divider.setFixedWidth(2)
        divider = self.divider

        # Coluna 3: Gráfico
        self.column3_frame = QFrame()
        self.column3_frame.setObjectName("column_3")
        column3_frame = self.column3_frame
        column3_layout = QVBoxLayout(column3_frame)
        column3_layout.addWidget(QLabel("Gráfico"))
        column3_layout.addStretch()

        columns_23_layout.addWidget(column2_frame)
        columns_23_layout.addWidget(divider)
        columns_23_layout.addWidget(column3_frame)

        grid_layout.addWidget(columns_23_frame, 0, 1, 1, 2)
        grid_layout.setColumnStretch(0, 1)
        grid_layout.setColumnStretch(1, 2)

        return grid_container

    def create_lower_grid(self):
        """Cria a grid inferior com calendário."""
        self.lower_grid_frame = QFrame()
        self.lower_grid_frame.setObjectName("lower_grid")
        grid_container = self.lower_grid_frame

        layout = QVBoxLayout(grid_container)
        self.calendar_dashboard = CalendarDashboard()
        self.calendar_dashboard.setFixedHeight(350)
        layout.addWidget(self.calendar_dashboard)

        return grid_container


class MainView(QMainWindow):
    """View principal da aplicação."""

    def __init__(self, viewmodel: MainViewModel | None = None, parent=None):
        super().__init__(parent)

        self.setWindowTitle("MeMap Pro - PySide6 + qasync")
        self.showMaximized()

        # Dependency Injection - ViewModel
        self._viewmodel = viewmodel or MainViewModel()

        # Inicializa gerenciadores
        self.style_manager = StyleManager()
        self._theme_manager = self._viewmodel.get_theme_manager()

        # Aplica tema inicial
        self._apply_theme()

        # Registra callback para atualizar quando tema mudar
        self._theme_manager.register_callback(self._apply_theme)

        # Cria widgets principais (injetando ThemeManager no Navbar)
        self.sidebar = Sidebar()
        self.navbar = Navbar(self._theme_manager)
        self.footer = Footer()

        # Container principal
        self.main_container = QWidget()
        self.main_layout = QVBoxLayout(self.main_container)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        # Layout do conteúdo
        self.content_layout = QHBoxLayout()
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)

        # Área de conteúdo principal
        self.content_area = QStackedWidget()
        self.content_area.setObjectName("main_content")

        # Páginas
        self.dashboard_page = DashboardPage()
        self.pages = {
            "dashboard": self.dashboard_page,
            "wizard": GuidedFormWizard(),
            "calendar": QWidget(), # Placeholder
            "tasks": QWidget(), # Placeholder
            "analytics": QWidget(), # Placeholder
            "settings": QWidget(), # Placeholder
        }

        # Adiciona páginas ao stacked widget
        for name, page in self.pages.items():
            self.content_area.addWidget(page)

        # Adiciona widgets ao layout
        self.content_layout.addWidget(self.sidebar)
        self.content_layout.addWidget(self.content_area)

        self.main_layout.addWidget(self.navbar)
        self.main_layout.addLayout(self.content_layout)
        self.main_layout.addWidget(self.footer)

        self.setCentralWidget(self.main_container)

        # FASE 3.3: Criar CalendarViewModel compartilhado e conectar signals
        from src.db.session_manager import SessionManager
        from src.repositories.tabela_taxas_repository import TabelaTaxasRepository
        from src.frontend.viewmodels import CalendarViewModel

        session = SessionManager.get_instance().get_session()
        repository = TabelaTaxasRepository(session)
        self.calendar_viewmodel = CalendarViewModel(repository)

        # Injetar ViewModel no CalendarDashboard
        self.dashboard_page.calendar_dashboard._viewmodel = self.calendar_viewmodel
        self.dashboard_page.calendar_dashboard.calendar._viewmodel = self.calendar_viewmodel

        # Conectar signal day_saved do Wizard ao Calendar
        self.pages["wizard"]._viewmodel.day_saved.connect(
            lambda date, success: self.calendar_viewmodel.mark_day_saved(date) if success else self.calendar_viewmodel.mark_day_deleted(date)
        )

        # Conectar signal data_modified do Wizard ao Calendar
        self.pages["wizard"]._viewmodel.data_modified.connect(
            lambda has_changes: self._on_wizard_data_modified(has_changes)
        )

        # Inicializa o Controller para mediar Calendário -> Wizard
        self.calendar_controller = CalendarController(
            self.dashboard_page.calendar_dashboard,
            self.pages["wizard"],
            self
        )

        # Conecta o progresso do Wizard ao Footer
        self.pages["wizard"].loading_progress.connect(self.footer.set_progress)
        self.pages["wizard"]._viewmodel.saving_progress.connect(self.footer.set_progress)

        # Conecta sinais
        self._connect_signals()

    def _apply_theme(self) -> None:
        """Aplica o tema atual a todos os componentes."""
        # Aplica stylesheet principal
        self.setStyleSheet(self.style_manager.get_main_stylesheet())

    def _on_wizard_data_modified(self, has_changes: bool) -> None:
        """Callback quando dados do Wizard são modificados.

        FASE 3.3: Marca dia como modificado no calendário se há mudanças.

        Args:
            has_changes: Se há mudanças não salvas
        """
        if has_changes:
            # Obter data selecionada do Wizard
            wizard = self.pages["wizard"]
            if hasattr(wizard, "_selected_date") and wizard._selected_date:
                self.calendar_viewmodel.mark_day_modified(wizard._selected_date)

    def _connect_signals(self):
        """Conecta os sinais da interface."""
        # Conecta UI -> ViewModel (delegação)
        self.sidebar.page_changed.connect(self._on_page_changed)
        self.dashboard_page.request_page_change.connect(self._on_page_changed)
        self.navbar.theme_toggle_requested.connect(self._on_theme_toggle_requested)

        # Conecta ViewModel -> UI (reação)
        self._viewmodel.current_page_changed.connect(self._on_viewmodel_page_changed)
        self._viewmodel.theme_changed.connect(self._on_viewmodel_theme_changed)

    @Slot(str)
    def _on_page_changed(self, page_name: str):
        """Delega navegação ao ViewModel."""
        self._viewmodel.navigate_to(page_name)  # type: ignore

    @Slot(str)
    def _on_viewmodel_page_changed(self, page_name: str):
        """Callback quando o ViewModel notifica mudança de página."""
        titles = {
            "dashboard": "Dashboard",
            "wizard": "Formulário Guiado",
            "calendar": "Calendário",
            "tasks": "Tarefas",
            "analytics": "Análises",
            "settings": "Configurações",
        }

        self.navbar.set_page_title(titles.get(page_name, "Página"))
        self.sidebar.set_active_page(page_name)
        self.content_area.setCurrentWidget(self.pages[page_name])

    @Slot()
    def _on_theme_toggle_requested(self):
        """Delega mudança de tema ao ViewModel."""
        self._viewmodel.toggle_theme()

    @Slot(object)
    def _on_viewmodel_theme_changed(self, theme: Theme):
        """Callback quando o ViewModel notifica mudança de tema."""
        # Atualiza botão do navbar
        self.navbar._update_theme_button()

    @property
    def viewmodel(self) -> MainViewModel:
        """Retorna o ViewModel (para testes e depuração)."""
        return self._viewmodel
