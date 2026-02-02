"""
Main View da aplicação com sidebar, navbar e footer.
Implementa a arquitetura principal da interface com nova estrutura de grids.
"""

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QCalendarWidget,
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

from src.frontend.styles.styles import StyleManager
from src.frontend.styles.component_styles import (
    SidebarStyles,
    NavbarStyles,
    FooterStyles,
    DashboardPageStyles,
    CalendarWidgetStyles,
)
from src.frontend.views.wizard_view import GuidedFormWizard
from src.frontend.views.calendar_dashboard import CalendarDashboard
from src.frontend.views.controller import CalendarController


class SidebarButton(QPushButton):
    """Botão customizado para o sidebar."""

    def __init__(self, text: str, icon: str = "", parent=None):
        super().__init__(text, parent)
        self.setProperty("sidebar_button", True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
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

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(16, 16, 16, 16)
        self.main_layout.setSpacing(8)

        # Título
        self.title_label = QLabel("MeMap Pro")
        self.title_label.setObjectName("sidebar_title")
        self.title_label.setStyleSheet(SidebarStyles.get_title_style())

        # Botões de navegação
        self.btn_dashboard = SidebarButton("📊 Dashboard")
        self.btn_dashboard.clicked.connect(
            lambda: self._on_page_changed("dashboard")
        )

        self.btn_wizard = SidebarButton("📝 Novo Formulário")
        self.btn_wizard.clicked.connect(
            lambda: self._on_page_changed("wizard")
        )

        self.btn_calendar = SidebarButton("📅 Calendário")
        self.btn_calendar.clicked.connect(
            lambda: self._on_page_changed("calendar")
        )

        self.btn_tasks = SidebarButton("✅ Tarefas")
        self.btn_tasks.clicked.connect(lambda: self._on_page_changed("tasks"))

        self.btn_analytics = SidebarButton("📈 Análises")
        self.btn_analytics.clicked.connect(
            lambda: self._on_page_changed("analytics")
        )

        self.btn_settings = SidebarButton("⚙️ Configurações")
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

        # Define Dashboard como página inicial
        self.set_active_page("dashboard")

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

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("navbar")

        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 8, 16, 8)
        self.main_layout.setSpacing(16)

        # Título da página
        self.page_title = QLabel("Dashboard")
        self.page_title.setObjectName("page_title")
        self.page_title.setStyleSheet(NavbarStyles.get_page_title_style())

        # Espaço flexível
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        # Status da aplicação
        self.status_label = QLabel("Pronto")
        self.status_label.setObjectName("status_label")
        self.status_label.setStyleSheet(NavbarStyles.get_status_label_style())

        # Adiciona widgets ao layout
        self.main_layout.addWidget(self.page_title)
        self.main_layout.addWidget(spacer)
        self.main_layout.addWidget(self.status_label)

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

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(16)

        # Título
        title = QLabel("Dashboard Principal")
        title.setStyleSheet(DashboardPageStyles.get_title_style())

        # Descrição
        description = QLabel(
            "Bem-vindo ao MeMap Pro! Sistema de gerenciamento com interface moderna."
        )
        description.setStyleSheet(DashboardPageStyles.get_description_style())

        # Grid Superior
        self.upper_grid = self.create_upper_grid()

        # Grid Inferior - Calendário
        self.lower_grid = self.create_lower_grid()

        # Adiciona widgets ao layout principal
        self.main_layout.addWidget(title)
        self.main_layout.addWidget(description)
        self.main_layout.addWidget(self.upper_grid)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.lower_grid)

    def create_upper_grid(self):
        """Cria a grid superior com 3 colunas."""
        grid_container = QFrame()
        grid_container.setObjectName("upper_grid")
        grid_container.setStyleSheet("""
            QFrame#upper_grid {
                background-color: #252526;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 16px;
            }
        """)

        grid_layout = QGridLayout(grid_container)
        grid_layout.setSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)

        # ===== COLUNA 1: Botões =====
        column1_frame = QFrame()
        column1_frame.setObjectName("column_1")
        column1_frame.setStyleSheet("""
            QFrame#column_1 {
                background-color: #2D2D30;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 12px;
                margin-right: 8px;
            }
        """)

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
        columns_23_frame = QFrame()
        columns_23_frame.setObjectName("columns_23")
        columns_23_frame.setStyleSheet("""
            QFrame#columns_23 {
                background-color: #2D2D30;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)

        columns_23_layout = QHBoxLayout(columns_23_frame)
        columns_23_layout.setSpacing(0)
        columns_23_layout.setContentsMargins(0, 0, 0, 0)

        # Coluna 2: Dados
        column2_frame = QFrame()
        column2_frame.setObjectName("column_2")
        column2_frame.setStyleSheet("QFrame#column_2 { background-color: #2D2D30; border: none; padding: 12px; }")
        column2_layout = QVBoxLayout(column2_frame)
        column2_layout.addWidget(QLabel("Dados"))
        column2_layout.addStretch()

        # Divisor
        divider = QFrame()
        divider.setFixedWidth(2)
        divider.setStyleSheet("background: #333;")

        # Coluna 3: Gráfico
        column3_frame = QFrame()
        column3_frame.setObjectName("column_3")
        column3_frame.setStyleSheet("QFrame#column_3 { background-color: #2D2D30; border: none; padding: 12px; }")
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
        grid_container = QFrame()
        grid_container.setObjectName("lower_grid")
        grid_container.setStyleSheet("""
            QFrame#lower_grid {
                background-color: #252526;
                border: 1px solid #333;
                border-radius: 12px;
                padding: 15px;
            }
        """)

        layout = QVBoxLayout(grid_container)
        self.calendar_dashboard = CalendarDashboard()
        self.calendar_dashboard.setFixedHeight(350)
        layout.addWidget(self.calendar_dashboard)

        return grid_container


class MainView(QMainWindow):
    """View principal da aplicação."""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("MeMap Pro - PySide6 + qasync")
        self.showMaximized()

        # Inicializa estilos
        self.style_manager = StyleManager()
        self.setStyleSheet(self.style_manager.get_main_stylesheet())

        # Cria widgets principais
        self.sidebar = Sidebar()
        self.navbar = Navbar()
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

        # Inicializa o Controller para mediar Calendário -> Wizard
        self.calendar_controller = CalendarController(
            self.dashboard_page.calendar_dashboard,
            self.pages["wizard"],
            self
        )

        # Conecta o progresso do Wizard ao Footer
        self.pages["wizard"].loading_progress.connect(self.footer.set_progress)

        # Conecta sinais
        self._connect_signals()

    def _connect_signals(self):
        """Conecta os sinais da interface."""
        self.sidebar.page_changed.connect(self._on_page_changed)
        self.dashboard_page.request_page_change.connect(self._on_page_changed)

    @Slot(str)
    def _on_page_changed(self, page_name: str):
        """Callback quando a página é alterada."""
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
