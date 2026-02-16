"""
Interface do formulário guiado (Wizard) para o MeMap Pro.
Implementa a navegação entre páginas e a estrutura de grids solicitada.
"""

import asyncio
import logging
from typing import Final

from PySide6.QtCore import QDate, Qt, Signal, Slot
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFrame,
    QGraphicsOpacityEffect,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy.orm.session import Session

from src.common.constants import ZonaTrabalho
from src.common.themes import ThemeManager
from src.common.themes.colors import ColorPalette
from src.common.utils.validation import validate_positive_int
from src.db.models.base_mixin import EstadoDocumento
from src.frontend.components.charts import VerticalBarChart
from src.frontend.styles.component_styles import NavbarStyles
from src.frontend.viewmodels.wizard_view_model import WizardViewModel
from src.frontend.views.recibos_table import RecibosTableWidget
from src.frontend.views.wizard_logic import (
    FormPage1Data,
    ValidationResult,
)

logger: logging.Logger = logging.getLogger(__name__)

# Simulação de imports do módulo 'common'
# from common.base import BaseFormPage
# from common.0styles import AppColors


# Constantes de Layout
INPUT_WIDTH: Final[int] = 60

class WizardPage1(QWidget):
    """Primeira página do formulário guiado.

    REFATORAÇÃO MVVM:
    - View apenas gerencia UI e captura entrada
    - ViewModel gerencia validação e lógica de negócio
    """

    submitted = Signal(dict)

    def __init__(self, viewmodel: WizardViewModel, parent: QWidget | None = None) -> None:
        """Inicializa a página com ViewModel.

        Args:
            viewmodel: WizardViewModel para gerenciar dados e lógica
            parent: Widget pai
        """
        super().__init__(parent)
        self._viewmodel: WizardViewModel = viewmodel
        self.recibos_table: RecibosTableWidget | None = None
        self.theme_manager = ThemeManager()
        self._current_date: QDate | None = None  # Data atual sendo editada
        self._is_loading_data: bool = False  # Flag para prevenir auto-updates durante carregamento

        # Conecta sinais do ViewModel → View
        self._viewmodel.resumo_updated.connect(self.update_resumo_financeiro)
        self._viewmodel.validation_error.connect(self._show_validation_error)

        self._init_ui()

    def set_current_date(self, date: QDate) -> None:
        """Define a data atual sendo editada.

        Args:
            date: Data do dia atual
        """
        self._current_date = date

    def _init_ui(self) -> None:
        """Inicializa a interface com duas grids (superior e inferior)."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # --- Grid Superior (Dividida em 2 colunas, cada uma com 4 linhas) ---
        self.upper_frame = QFrame()
        self.upper_frame.setObjectName("upper_grid")
        self.upper_layout = QGridLayout(self.upper_frame)
        self.upper_layout.setContentsMargins(10, 10, 10, 10)
        self.upper_layout.setSpacing(15)

        # Configuração das colunas (70% formulário, 30% resumo)
        self.upper_layout.setColumnStretch(0, 7)
        self.upper_layout.setColumnStretch(1, 3)

        # Coluna Esquerda (Superior)
        self._setup_left_column()

        # Coluna Direita (Superior) - Espaço reservado para futuras perguntas
        self._setup_right_column()

        # --- Grid Central (Tabela de Recibos) ---
        self.recibos_table = RecibosTableWidget()
        self.recibos_table.setVisible(False)  # Oculta até ter dados válidos
        self.recibos_table.data_changed.connect(self._on_table_data_changed)

        # --- Grid Inferior ---
        self.lower_frame = QFrame()
        self.lower_frame.setObjectName("lower_grid")
        self.lower_layout = QVBoxLayout(self.lower_frame)

        # Botão de navegação "Próximo" (centralizado)
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        self.btn_next = QPushButton("Próximo ➔")
        self.btn_next.setFixedWidth(120)
        self.btn_next.setMinimumHeight(40)
        self.btn_next.clicked.connect(self._on_next_clicked)
        buttons_layout.addWidget(self.btn_next)
        buttons_layout.addStretch()

        self.lower_layout.addLayout(buttons_layout)

        # Adiciona as grids ao layout principal dividindo o espaço total
        self.main_layout.addWidget(self.upper_frame, 0)  # Fixa no topo
        self.main_layout.addWidget(self.recibos_table, 3)  # Ocupa mais espaço
        self.main_layout.addWidget(self.lower_frame, 0)  # Fixa no fundo

        # Conecta signals dos inputs para atualizar tabela E ViewModel
        self.input_qtd.textChanged.connect(self._on_input_changed)
        self.input_inicio.textChanged.connect(self._on_input_changed)
        self.input_fim.textChanged.connect(self._on_input_changed)

        # Conecta inputs ao ViewModel
        self.input_qtd.textChanged.connect(
            lambda text: self._viewmodel.set_form_field("quantidade_recibos", text)
        )
        self.input_inicio.textChanged.connect(
            lambda text: self._viewmodel.set_form_field("recibo_inicio", text)
        )
        self.input_fim.textChanged.connect(
            lambda text: self._viewmodel.set_form_field("recibo_fim", text)
        )

        # Inicializa o resumo financeiro com valores zerados
        self.update_resumo_financeiro(0.0, 0.0)

    def _setup_left_column(self) -> None:
        """Configura a coluna esquerda da grid superior (2 linhas úteis)."""

        # 1ª Linha: Recibos (Quantidade, Início, Fim) + Serv. Interno + Botão Limpar
        row1_container = QWidget()
        row1_layout = QHBoxLayout(row1_container)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(10)

        self.input_qtd: QLineEdit = self._create_input(
            "Quantos recibos são?", row1_layout
            )
        self.input_inicio: QLineEdit = self._create_input(
            "Início", row1_layout
            )
        self.input_inicio.setFixedWidth(69)  # 15% maior que 60px

        self.input_fim: QLineEdit = self._create_input("Fim", row1_layout)
        self.input_fim.setFixedWidth(69)  # 15% maior que 60px

        # Checkbox Serv. Interno
        self.checkbox_serv_interno = QCheckBox("Serv. Interno")
        row1_layout.addWidget(self.checkbox_serv_interno)

        # Botão Limpar Dados (substitui Total KM) - apenas ícone, sem fundo
        self.btn_limpar = QPushButton("🗑️")
        self.btn_limpar.setFixedSize(35, 30)
        self.btn_limpar.setToolTip("Limpar todos os dados do formulário e tabela")
        self.btn_limpar.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 18px;
                padding: 2px;
                color: #757575;
            }
            QPushButton:hover {
                background-color: #ffebee;
                border-radius: 4px;
                color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #ffcdd2;
            }
        """)
        self.btn_limpar.clicked.connect(self._on_limpar_clicked)
        row1_layout.addWidget(self.btn_limpar)

        row1_layout.addStretch()

        self.upper_layout.addWidget(row1_container, 0, 0)

        # 2ª Linha: Gasoleo + campos condicionais + campos sempre visíveis
        row2_container = QWidget()
        row2_layout = QHBoxLayout(row2_container)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(10)

        # Checkbox Gasoleo
        self.checkbox_gasoleo = QCheckBox("Gasoleo")
        row2_layout.addWidget(self.checkbox_gasoleo)

        # Campos condicionais (aparecem apenas se gasoleo marcado)
        self.input_gasoleo_valor: QLineEdit = self._create_input(
            "Valor", row2_layout
            )
        self.input_gasoleo_valor.setFixedWidth(69)  # 15% maior que 60px
        self.input_gasoleo_valor.setPlaceholderText("0,00€")

        self.input_gasoleo_litros: QLineEdit = self._create_input(
            "Litros", row2_layout
            )
        self.input_gasoleo_litros.setFixedWidth(69)  # 15% maior que 60px
        self.input_gasoleo_litros.setPlaceholderText("0.00L")

        # Campos sempre visíveis (monetários)
        self.input_almoco: QLineEdit = self._create_input(
            "Almoço", row2_layout
            )
        self.input_almoco.setFixedWidth(69)  # 15% maior que 60px
        self.input_almoco.setPlaceholderText("0,00€")

        self.input_despesas_gerais: QLineEdit = self._create_input(
            "Despesas Gerais", row2_layout
            )
        self.input_despesas_gerais.setFixedWidth(69)  # 15% maior que 60px
        self.input_despesas_gerais.setPlaceholderText("0,00€")

        row2_layout.addStretch()

        # Inicialmente oculta apenas os campos condicionais do gasoleo
        self.input_gasoleo_valor.setVisible(False)
        self.input_gasoleo_litros.setVisible(False)

        # Conecta o checkbox para mostrar/ocultar campos
        self.checkbox_gasoleo.stateChanged.connect(self._on_gasoleo_changed)

        # FASE 4: Conecta checkbox Serviço Interno
        self.checkbox_serv_interno.stateChanged.connect(self._on_servico_interno_changed)

        self.upper_layout.addWidget(row2_container, 1, 0)

        # Linhas 3 e 4: Reservadas
        self.upper_layout.addWidget(QLabel(" "), 2, 0)
        self.upper_layout.addWidget(QLabel(" "), 3, 0)

    def _setup_right_column(self) -> None:
        """Configura a coluna direita com o resumo financeiro do dia."""
        # Container principal do resumo
        resumo_container = QFrame()
        resumo_container.setObjectName("resumo_financeiro")
        resumo_layout = QVBoxLayout(resumo_container)
        resumo_layout.setContentsMargins(15, 10, 15, 10)
        resumo_layout.setSpacing(8)

        # Título do resumo
        titulo_resumo = QLabel("📊 Resumo do Dia")
        titulo_resumo.setStyleSheet("font-weight: bold; font-size: 13px;")
        titulo_resumo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        resumo_layout.addWidget(titulo_resumo)

        # Gráfico de barras PyQtGraph
        self.chart_resumo = VerticalBarChart(
            parent=self, theme_manager=self.theme_manager
        )
        resumo_layout.addWidget(self.chart_resumo)

        # Linha divisória
        divider = QFrame()
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        resumo_layout.addWidget(divider)

        # Label de lucro
        self.label_lucro = QLabel("💰 Lucro: €0,00")
        self.label_lucro.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_lucro.setStyleSheet("font-weight: bold; font-size: 13px;")
        resumo_layout.addWidget(self.label_lucro)

        resumo_layout.addStretch()

        # Adiciona o resumo à grid (ocupa todas as 4 linhas)
        self.upper_layout.addWidget(resumo_container, 0, 1, 4, 1)

    def _create_input(self, label_text: str, layout: QHBoxLayout) -> QLineEdit:
        """Cria um par Label + InputBox com largura fixa de 60px."""
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setFixedWidth(INPUT_WIDTH)
        input_field.setPlaceholderText("0")

        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def _create_chosebox(
            self, label_text: str,
            layout: QHBoxLayout
            ) -> QComboBox:
        """Cria um par Label + ChoseBox (ComboBox)."""
        label = QLabel(label_text)
        combo = QComboBox()
        combo.setMinimumWidth(100)

        # Popula com as zonas do Enum
        for zona in ZonaTrabalho:
            combo.addItem(zona.value, zona)

        layout.addWidget(label)
        layout.addWidget(combo)
        return combo

    def _on_input_changed(self) -> None:
        """Callback quando inputs de quantidade/início/fim mudam.

        Atualiza a tabela de recibos se os dados forem válidos.
        """
        qtd_text: str = self.input_qtd.text().strip()
        inicio_text: str = self.input_inicio.text().strip()
        fim_text: str = self.input_fim.text().strip()

        # Verifica se todos têm valor
        if not all([qtd_text, inicio_text, fim_text]):
            if self.recibos_table:
                self.recibos_table.setVisible(False)
            return

        # Valida se são inteiros positivos
        if not all([
            validate_positive_int(qtd_text),
            validate_positive_int(inicio_text),
            validate_positive_int(fim_text)
        ]):
            if self.recibos_table:
                self.recibos_table.setVisible(False)
            return

        # Converte valores
        try:
            quantidade = int(qtd_text)
            inicio = int(inicio_text)
            fim = int(fim_text)

            # Valida range
            if fim < inicio or quantidade <= 0:
                if self.recibos_table:
                    self.recibos_table.setVisible(False)
                return

            # Atualiza tabela
            if self.recibos_table:
                self.recibos_table.rebuild_table(quantidade, inicio, fim)
                self.recibos_table.setVisible(True)

        except ValueError:
            if self.recibos_table:
                self.recibos_table.setVisible(False)

    def _on_gasoleo_changed(self, state: int) -> None:
        """Callback quando checkbox Gasoleo muda de estado.

        Mostra/oculta apenas Valor e Litros baseado no estado do checkbox.
        Almoço e Despesas Gerais ficam sempre visíveis.

        Args:
            state: Estado do checkbox (Qt.CheckState.Checked ou Qt.CheckState.Unchecked)
        """
        is_checked = state == Qt.CheckState.Checked.value

        # Mostra/oculta apenas campos condicionais do gasoleo
        self.input_gasoleo_valor.setVisible(is_checked)
        self.input_gasoleo_litros.setVisible(is_checked)

        # Limpa os campos quando ocultos
        if not is_checked:
            self.input_gasoleo_valor.clear()
            self.input_gasoleo_litros.clear()

    def _on_servico_interno_changed(self, state: int) -> None:
        """Handler quando checkbox de Serviço Interno muda.

        FASE 4 (CORRIGIDO): Ativa/desativa modo Serviço Interno na tabela
        e mostra/oculta a tabela independentemente do formulário.

        Args:
            state: Estado do checkbox (Qt.CheckState.Checked ou Qt.CheckState.Unchecked)
        """
        is_checked: bool = state == Qt.CheckState.Checked.value

        # Atualizar ViewModel principal
        self._viewmodel.set_form_field("servico_interno", is_checked)

        # Atualizar RecibosTable ViewModel + Mostrar/Ocultar tabela
        if self.recibos_table:
            # Atualizar estado de Serviço Interno (cria/remove linhas)
            self.recibos_table.viewmodel.set_servico_interno(is_checked)

            # FASE 4: Mostrar tabela quando Serviço Interno ativo
            # (independente do formulário)
            if is_checked:
                self.recibos_table.setVisible(True)
            else:
                # Ocultar apenas se não há dados do formulário
                # (verificar se tabela tem dados de recibos)
                if self.recibos_table.viewmodel.is_empty:
                    self.recibos_table.setVisible(False)

        logger.info(f"Serviço Interno: {'ATIVADO' if is_checked else 'DESATIVADO'}")

    def _on_limpar_clicked(self) -> None:
        """Handler quando botão Limpar é clicado.

        NOVO: Elimina o dia da BD imediatamente e volta ao estado inicial.
        O dia fica como se nunca tivesse sido criado.
        """
        from PySide6.QtWidgets import QMessageBox
        import asyncio

        # Confirmar com usuário
        reply = QMessageBox.question(
            self,
            "Confirmar Limpeza",
            "Tem certeza que deseja limpar todos os dados?\n\n"
            "Esta ação irá:\n"
            "• Limpar todos os campos do formulário\n"
            "• Limpar toda a tabela de recibos\n"
            "• ELIMINAR IMEDIATAMENTE os dados da BD\n"
            "• O dia volta ao estado inicial (novo)\n\n"
            "Esta ação não pode ser revertida!",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Chamar método async
        loop = asyncio.get_event_loop()
        loop.create_task(self._limpar_async())

    async def _limpar_async(self) -> None:
        """Método async para limpar dados e eliminar da BD."""
        from src.frontend.components.notifications import NotificationManager

        # 1. Eliminar dia da BD (passar data atual)
        success, message = await self._viewmodel.delete_current_day(self._current_date)

        if not success:
            NotificationManager.instance().error(
                f"Não foi possível eliminar o dia da BD: {message}"
            )
            return

        # 2. Limpar UI (formulário e tabela)
        self.blockSignals(True)

        # Limpar campos do formulário
        self.input_qtd.clear()
        self.input_inicio.clear()
        self.input_fim.clear()
        self.checkbox_serv_interno.setChecked(False)
        self.checkbox_gasoleo.setChecked(False)
        self.input_gasoleo_valor.clear()
        self.input_gasoleo_litros.clear()

        # Limpar tabela
        if self.recibos_table:
            self.recibos_table.clear_table()
            self.recibos_table.setVisible(False)

        self.blockSignals(False)

        logger.info("✅ Dia eliminado da BD e UI limpa")

        from src.frontend.components.notifications import NotificationManager
        NotificationManager.instance().success(
            f"{message} O dia volta ao estado inicial."
        )

    def _on_table_data_changed(self) -> None:
        """Callback quando dados da tabela mudam.

        NOVA FUNCIONALIDADE: Auto-atualiza campos do formulário (quantidade,
        início, fim) baseado nos dados reais da tabela.
        """
        # CRÍTICO: Ignorar mudanças durante carregamento de dados
        # Evita auto-updates com dados transitórios/incorretos
        if self._is_loading_data:
            logger.debug("⏭️ Auto-update ignorado (carregamento em progresso)")
            return

        # Atualiza ViewModel com novos dados da tabela
        if self.recibos_table:
            table_data: list[dict[str, str | dict[str, str | bool]]] = self.recibos_table.get_table_data()
            self._viewmodel.set_table_data(table_data)

            # NOVA FUNCIONALIDADE: Recalcular campos do formulário baseado na tabela
            self._update_form_from_table(table_data)

            # Recalcula resumo financeiro
            self._viewmodel.calculate_resumo_financeiro()

    def _update_form_from_table(self, table_data: list[dict[str, str | dict[str, str | bool]]]) -> None:
        """Atualiza campos do formulário baseado nos dados da tabela.

        Recalcula quantidade, recibo início e recibo fim automaticamente
        quando a tabela é editada manualmente.

        Args:
            table_data: Dados atuais da tabela
        """
        if not table_data:
            return

        # Extrair números de recibos válidos (não vazios e não "0")
        recibos: list[int] = []
        for row in table_data:
            recibo_str = row.get("Recibo", "")
            if recibo_str and str(recibo_str).strip() and str(recibo_str) != "0":
                try:
                    recibo_num = int(recibo_str)
                    if recibo_num > 0:
                        recibos.append(recibo_num)
                except (ValueError, TypeError):
                    continue

        if not recibos:
            return

        # Calcular valores
        quantidade = len(recibos)
        recibo_inicio = min(recibos)
        recibo_fim = max(recibos)

        # Atualizar campos do formulário
        self.input_qtd.setText(str(quantidade))
        self.input_inicio.setText(str(recibo_inicio))
        self.input_fim.setText(str(recibo_fim))

        logger.info(f"Formulário auto-atualizado: Qtd={quantidade}, Início={recibo_inicio}, Fim={recibo_fim}")

    def update_resumo_financeiro(self, premio: float, gastos: float) -> None:
        """Atualiza o resumo financeiro com os valores de prémio e gastos.

        Args:
            premio: Valor do prémio do dia em euros
            gastos: Valor dos gastos do dia em euros
        """
        # Calcula lucro
        lucro: float = premio - gastos

        # Atualiza o gráfico
        self.chart_resumo.set_data(premio, gastos)

        # Atualiza label de lucro com cor apropriada
        lucro_text: str = f"€{abs(lucro):.2f}".replace(".", ",")
        if lucro >= 0:
            self.label_lucro.setText(f"💰 Lucro: {lucro_text} ✅")
            self.label_lucro.setStyleSheet(
                "font-weight: bold; font-size: 13px; color: #28a745;"
            )
        else:
            self.label_lucro.setText(f"⚠️ Prejuízo: {lucro_text}")
            self.label_lucro.setStyleSheet(
                "font-weight: bold; font-size: 13px; color: #dc3545;"
            )

    def _on_next_clicked(self) -> None:
        """Coleta dados, valida através do ViewModel e emite sinal."""
        # Atualiza todos os campos no ViewModel
        self._viewmodel.set_form_field("quantidade_recibos", self.input_qtd.text())
        self._viewmodel.set_form_field("recibo_inicio", self.input_inicio.text())
        self._viewmodel.set_form_field("recibo_fim", self.input_fim.text())
        self._viewmodel.set_form_field("servico_interno", self.checkbox_serv_interno.isChecked())
        self._viewmodel.set_form_field("gasoleo", self.checkbox_gasoleo.isChecked())
        self._viewmodel.set_form_field(
            "gasoleo_valor",
            self.input_gasoleo_valor.text() if self.checkbox_gasoleo.isChecked() else ""
        )
        self._viewmodel.set_form_field(
            "gasoleo_litros",
            self.input_gasoleo_litros.text() if self.checkbox_gasoleo.isChecked() else ""
        )
        self._viewmodel.set_form_field("almoco", self.input_almoco.text())
        self._viewmodel.set_form_field("despesas_gerais", self.input_despesas_gerais.text())

        # Atualiza dados da tabela no ViewModel
        if self.recibos_table and self.recibos_table.isVisible():
            table_data: list[dict[str, str | dict[str, str | bool]]] = self.recibos_table.get_table_data()
            self._viewmodel.set_table_data(table_data)

        # Delega validação ao ViewModel
        result: ValidationResult = self._viewmodel.validate_page_1()

        if result.is_valid:
            # Reset visual em caso de sucesso
            self.input_qtd.setStyleSheet("")

            # Prepara dados para emitir
            form_data = dict(result.data) if result.data else {}
            form_data["table_data"] = self._viewmodel.get_table_data()

            self.submitted.emit(form_data)
        else:
            # Erro já foi emitido pelo ViewModel via validation_error signal
            # View apenas atualiza UI
            pass

    def _show_validation_error(self, error_message: str) -> None:
        """Mostra erro de validação na UI.

        Args:
            error_message: Mensagem de erro
        """
        self.input_qtd.setToolTip(error_message)
        palette: ColorPalette = self.theme_manager.current_palette
        self.input_qtd.setStyleSheet(f"border: 1px solid {palette.error};")


class GuidedFormWizard(QWidget):
    """Widget principal que gerencia a navegação do formulário guiado."""

    # Sinal para atualizar o progresso (0-100)
    loading_progress = Signal(int)

    def __init__(self, viewmodel: WizardViewModel | None = None, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._is_loading = False
        self._current_state: EstadoDocumento = EstadoDocumento.RASCUNHO
        self._selected_date: QDate | None = None  # FASE 2: Data selecionada

        # Dependency Injection - ViewModel
        self._viewmodel: WizardViewModel = viewmodel or WizardViewModel()

        # FASE 2.1: Inicializar Repository e injetar no ViewModel
        from src.db.session_manager import SessionManager
        from src.repositories.tabela_taxas_repository import TabelaTaxasRepository

        session: Session = SessionManager.get_instance().get_session()
        repository = TabelaTaxasRepository(session)
        self._viewmodel.set_repository(repository)

        # Theme manager
        self.theme_manager = ThemeManager()
        self.theme_manager.register_callback(self._apply_theme)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 10, 20, 20)
        self.main_layout.setSpacing(10)

        # Header para mostrar a data selecionada (Estilo Navbar)
        self.header_frame = QFrame()
        self.header_frame.setObjectName("wizard_header")
        header_layout = QHBoxLayout(self.header_frame)

        self.date_label = QLabel("Selecione uma data no calendário")
        header_layout.addWidget(self.date_label)
        header_layout.addStretch()

        # FASE 2.2: Botão "Gravar Dia" no header
        self.btn_save_day = QPushButton("💾 Gravar Dia")
        self.btn_save_day.setFixedWidth(140)
        self.btn_save_day.setMinimumHeight(40)
        self.btn_save_day.clicked.connect(self._on_save_day_clicked)
        header_layout.addWidget(self.btn_save_day)

        self.main_layout.addWidget(self.header_frame)

        # Aplica tema inicial
        self._apply_theme()

        # FASE 2.3: Conectar signals do ViewModel para feedback visual
        self._viewmodel.day_saved.connect(self._on_day_saved)
        self._viewmodel.data_modified.connect(self._on_data_modified)

        self.stack = QStackedWidget()

        # Páginas do Wizard (injeta ViewModel)
        self.page1 = WizardPage1(self._viewmodel)
        self.page1.submitted.connect(self._next_page)

        self.page2 = QWidget() # Placeholder para a 2ª página
        p2_layout = QVBoxLayout(self.page2)
        p2_layout.addWidget(QLabel(
            "Página 2 - Em desenvolvimento"), 0,
            Qt.AlignmentFlag.AlignCenter
            )
        btn_back = QPushButton("⬅ Voltar")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        p2_layout.addWidget(btn_back, 0, Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        # FASE 2.5: Injetar repository no RecibosTableViewModel para validação
        if self.page1.recibos_table:
            self.page1.recibos_table.viewmodel.set_repository(repository)
            # Definir mês/ano atual (será atualizado ao selecionar data)
            current_date = QDate.currentDate()
            self.page1.recibos_table.viewmodel.set_current_date(current_date.month(), current_date.year())
            logger.info("Repository injetado no RecibosTableViewModel")

        self.main_layout.addWidget(self.stack)

    def _apply_theme(self) -> None:
        """Aplica o tema atual aos componentes do wizard."""
        palette: ColorPalette = self.theme_manager.current_palette

        # Atualiza o header
        self.header_frame.setStyleSheet(f"""
            QFrame#wizard_header {{
                background-color: {palette.background_secondary};
                border-bottom: 2px solid {palette.accent};
                border-radius: 8px;
                padding: 10px;
            }}
        """)

        # Atualiza o label da data
        self.date_label.setStyleSheet(NavbarStyles.get_page_title_style())

    # FASE 2.3: Feedback Visual (Header Verde/Amarelo)

    def _apply_saved_style(self) -> None:
        """Aplica estilo verde ao header quando dia é salvo."""
        self.header_frame.setStyleSheet("""
            QFrame#wizard_header {
                background-color: #d4edda;
                border-bottom: 3px solid #28a745;
                padding: 12px;
                border-radius: 4px;
            }
        """)

    def _apply_modified_style(self) -> None:
        """Aplica estilo amarelo ao header quando há modificações não salvas."""
        self.header_frame.setStyleSheet("""
            QFrame#wizard_header {
                background-color: #fff3cd;
                border-bottom: 3px solid #ffc107;
                padding: 12px;
                border-radius: 4px;
            }
        """)

    def _apply_default_style(self) -> None:
        """Aplica estilo padrão ao header (sem cores especiais)."""
        palette: ColorPalette = self.theme_manager.current_palette
        self.header_frame.setStyleSheet(f"""
            QFrame#wizard_header {{
                background-color: {palette.surface};
                border-bottom: 2px solid {palette.border};
                padding: 12px;
                border-radius: 4px;
            }}
        """)

    def _load_form_data_to_ui(self) -> None:
        """Carrega dados do formulário do ViewModel para a UI."""
        # Obter dados do ViewModel
        qtd = self._viewmodel.get_form_field("quantidade_recibos", "")
        inicio = self._viewmodel.get_form_field("recibo_inicio", "")
        fim = self._viewmodel.get_form_field("recibo_fim", "")
        servico_interno = self._viewmodel.get_form_field("servico_interno", False)
        gasoleo = self._viewmodel.get_form_field("gasoleo", False)

        # CRÍTICO: Bloquear signals para evitar reconstrução da tabela durante carregamento
        self.page1.input_qtd.blockSignals(True)
        self.page1.input_inicio.blockSignals(True)
        self.page1.input_fim.blockSignals(True)
        self.page1.checkbox_serv_interno.blockSignals(True)
        self.page1.checkbox_gasoleo.blockSignals(True)

        try:
            # Atualizar campos da UI
            self.page1.input_qtd.setText(str(qtd))
            self.page1.input_inicio.setText(str(inicio))
            self.page1.input_fim.setText(str(fim))
            self.page1.checkbox_serv_interno.setChecked(servico_interno)
            self.page1.checkbox_gasoleo.setChecked(gasoleo)

            logger.debug(f"✅ Dados do formulário carregados na UI (signals bloqueados): Qtd={qtd}, Inicio={inicio}, Fim={fim}")
        finally:
            # Desbloquear signals
            self.page1.input_qtd.blockSignals(False)
            self.page1.input_inicio.blockSignals(False)
            self.page1.input_fim.blockSignals(False)
            self.page1.checkbox_serv_interno.blockSignals(False)
            self.page1.checkbox_gasoleo.blockSignals(False)

    def _load_table_data_to_ui(self) -> None:
        """Carrega dados da tabela do ViewModel para a UI.

        CORRIGIDO: Usa load_data_from_saved para preservar recibos exatos,
        incluindo duplicados, em vez de rebuild_table que cria sequência.
        """
        table_data = self._viewmodel.get_table_data()

        if not table_data:
            logger.debug("Nenhum dado de tabela para carregar")
            return

        # Carregar dados preservando recibos exatos (incluindo duplicados)
        if self.page1.recibos_table:
            # Usar método específico para carregar dados salvos
            self.page1.recibos_table.viewmodel.load_data_from_saved(table_data)

            # CRÍTICO: Tornar tabela visível após carregar dados
            self.page1.recibos_table.setVisible(True)

            quantidade = len(table_data)
            logger.info(f"Tabela carregada com {quantidade} linhas exatas da BD (preservando duplicados) e tornada VISÍVEL")

    def _clear_form(self) -> None:
        """Limpa todos os campos do formulário."""
        self.page1.input_qtd.clear()
        self.page1.input_inicio.clear()
        self.page1.input_fim.clear()
        self.page1.checkbox_serv_interno.setChecked(False)
        self.page1.checkbox_gasoleo.setChecked(False)
        logger.debug("Formulário limpo")

    def _clear_table(self) -> None:
        """Limpa tabela de recibos."""
        if self.page1.recibos_table:
            self.page1.recibos_table.clear_table()
            self.page1.recibos_table.setVisible(False)
            logger.debug("Tabela limpa")

    @Slot(QDate, bool)
    def _on_day_saved(self, date: QDate, success: bool) -> None:
        """Callback quando dia é salvo ou eliminado no ViewModel.

        Args:
            date: Data salva/eliminada
            success: True se salvo, False se eliminado
        """
        if success:
            self._apply_saved_style()
            # Atualizar label com data
            date_str = date.toString("dd/MM/yyyy")
            self.date_label.setText(f"✅ {date_str} - Salvo com sucesso")
            logger.info(f"Feedback visual: Dia {date_str} salvo")
        else:
            # Dia foi eliminado - resetar para estilo padrão
            self._apply_default_style()
            date_str = date.toString("dd/MM/yyyy")
            self.date_label.setText(f"📅 {date_str}")
            logger.info(f"Feedback visual: Dia {date_str} resetado para estado inicial")

    @Slot(bool)
    def _on_data_modified(self, has_changes: bool) -> None:
        """Callback quando dados são modificados no ViewModel.

        Args:
            has_changes: Se há mudanças não salvas
        """
        if has_changes and hasattr(self, "_selected_date") and self._selected_date:
            self._apply_modified_style()
            date_str = self._selected_date.toString("dd/MM/yyyy")
            self.date_label.setText(f"⚠️ {date_str} - Não salvo")
            logger.debug(f"Feedback visual: Dia {date_str} modificado (não salvo)")

    def _next_page(self, data: FormPage1Data) -> None:
        """Avança para a próxima página do formulário."""
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)

    def _set_ui_enabled(self, enabled: bool) -> None:
        """Habilita/Desabilita a UI durante o carregamento."""
        self.stack.setEnabled(enabled)
        opacity: float = 1.0 if enabled else 0.5
        effect = QGraphicsOpacityEffect(self.stack)
        effect.setOpacity(opacity)
        self.stack.setGraphicsEffect(effect)

    @Slot()
    def _on_save_day_clicked(self) -> None:
        """Handler para salvar dia (inicia task assíncrona).

        FASE 2.2 (CORRIGIDO): Usa get_event_loop().create_task para compatibilidade com qasync.
        """
        logger.info("🟢🟢🟢 DEBUG BTN: Botão 'Gravar Dia' CLICADO! 🟢🟢🟢")

        # Verificar se data foi selecionada
        if not self._selected_date:
            logger.warning("🔴 DEBUG BTN: Nenhuma data selecionada!")
            return

        logger.info(f"🟢 DEBUG BTN: Data selecionada: {self._selected_date.toString('dd/MM/yyyy')}")

        # Criar task assíncrona no event loop correto (qasync)
        loop = asyncio.get_event_loop()
        logger.info(f"🟢 DEBUG BTN: Criando task assíncrona no event loop...")
        loop.create_task(self._save_day_async())
        logger.info(f"🟢 DEBUG BTN: Task criada com sucesso!")

    async def _save_day_async(self) -> None:
        """Método assíncrono para salvar dia na BD."""
        logger.info("🟡🟡🟡 DEBUG ASYNC: Método _save_day_async INICIADO! 🟡🟡🟡")

        # Desabilitar botão durante salvamento
        self.btn_save_day.setEnabled(False)
        self.btn_save_day.setText("⏳ Salvando...")
        logger.info("🟡 DEBUG ASYNC: Botão desabilitado")

        try:
            # Atualizar todos os campos no ViewModel a partir de page1
            logger.info("🟡 DEBUG ASYNC: Atualizando campos do formulário...")
            self._viewmodel.set_form_field("quantidade_recibos", self.page1.input_qtd.text())
            self._viewmodel.set_form_field("recibo_inicio", self.page1.input_inicio.text())
            self._viewmodel.set_form_field("recibo_fim", self.page1.input_fim.text())
            self._viewmodel.set_form_field("servico_interno", self.page1.checkbox_serv_interno.isChecked())
            self._viewmodel.set_form_field("gasoleo", self.page1.checkbox_gasoleo.isChecked())
            logger.info(f"🟡 DEBUG ASYNC: Campos atualizados. Qtd={self.page1.input_qtd.text()}, Inicio={self.page1.input_inicio.text()}")

            # Atualizar dados da tabela no ViewModel
            logger.info("🟡 DEBUG ASYNC: Obtendo dados da tabela...")
            if self.page1.recibos_table and self.page1.recibos_table.isVisible():
                table_data = self.page1.recibos_table.get_table_data()
                logger.info(f"🟡 DEBUG ASYNC: Tabela tem {len(table_data)} linhas")
                self._viewmodel.set_table_data(table_data)  # type: ignore
                logger.info(f"🟡 DEBUG ASYNC: Dados da tabela atualizados no ViewModel")
            else:
                logger.warning(f"🔴 DEBUG ASYNC: Tabela NÃO visível ou não existe!")

            # Chamar método de salvamento assíncrono
            logger.info(f"🟡 DEBUG ASYNC: Chamando save_current_day do ViewModel...")
            success, message = await self._viewmodel.save_current_day(self._selected_date)

            logger.info(f"🟡 DEBUG ASYNC: Retorno do ViewModel: success={success}, message={message}")

            if success:
                logger.info(f"✅✅✅ DEBUG ASYNC: DIA SALVO COM SUCESSO! ✅✅✅")
                logger.info(f"✅ Dia salvo: {message}")
                # Aplicar estilo verde ao header
                logger.info(f"🟡 DEBUG ASYNC: Aplicando estilo verde ao header...")
                self._apply_saved_style()
                date_str = self._selected_date.toString("dd/MM/yyyy")
                self.date_label.setText(f"✅ {date_str} - Salvo")
                logger.info(f"✅ DEBUG ASYNC: Feedback visual aplicado!")

                # Mostrar notificação de sucesso
                from src.frontend.components.notifications import NotificationManager
                NotificationManager.instance().success(
                    f"Dia {date_str} salvo com sucesso!"
                )
            else:
                logger.error(f"🔴🔴🔴 DEBUG ASYNC: SALVAMENTO FALHOU! 🔴🔴🔴")
                logger.error(f"❌ Erro ao salvar: {message}")

                # CRÍTICO: Mostrar diálogo de erro ao utilizador
                from src.frontend.components.notifications import NotificationManager
                NotificationManager.instance().error(message, duration=6000)

        except Exception as e:
            logger.error(f"🔴🔴🔴 DEBUG ASYNC: EXCEÇÃO CAPTURADA! 🔴🔴🔴")
            logger.error(f"❌ Exceção ao salvar dia: {e}", exc_info=True)

            # Mostrar erro ao utilizador
            from src.frontend.components.notifications import NotificationManager
            NotificationManager.instance().error(
                f"Erro ao salvar o dia: {str(e)}. Verifique os logs.",
                duration=6000
            )

        finally:
            # Reabilitar botão
            logger.info(f"🟡 DEBUG ASYNC: Reabilitando botão...")
            self.btn_save_day.setEnabled(True)
            self.btn_save_day.setText("💾 Gravar Dia")
            logger.info(f"🟡 DEBUG ASYNC: Método _save_day_async FINALIZADO")

    @Slot(QDate)
    def set_selected_date(self, date: QDate) -> None:
        """
        Slot que carrega dados da DB para a data selecionada.
        Cria tarefa assíncrona para compatibilidade com qasync event loop.
        """
        loop = asyncio.get_event_loop()
        loop.create_task(self._set_selected_date_async(date))

    async def _set_selected_date_async(self, date: QDate) -> None:
        """
        Implementação assíncrona do carregamento de dados para a data selecionada.
        Previne race conditions usando uma flag de loading.
        """
        # FASE 2: Guardar data selecionada
        self._selected_date = date

        # FASE 2.6: Atualizar data atual no RecibosTableViewModel para validação
        # CRÍTICO: Passa dia para ignorar duplicados do próprio dia ao editar
        if self.page1.recibos_table:
            self.page1.recibos_table.viewmodel.set_current_date(
                date.month(),
                date.year(),
                date.day()  # Ignora duplicados do próprio dia
            )

        if self._is_loading:
            logger.warning("Carregamento já em curso. Ignorando novo pedido.")
            return

        self._is_loading = True
        self._set_ui_enabled(False)
        self.loading_progress.emit(10)
        self.date_label.setText(
            f"⏳ A carregar dados para {date.toString('dd/MM/yyyy')}..."
            )

        try:
            # FASE 2.4: Carregar dados reais da BD
            self.loading_progress.emit(30)

            # Tentar carregar dados do dia da BD
            success, message = await self._viewmodel.load_day_data(date)

            self.loading_progress.emit(60)

            if success:
                # Dados carregados com sucesso
                logger.info(f"Dados carregados: {message}")

                # CRÍTICO: Ativar flag para prevenir auto-updates durante carregamento
                self.page1._is_loading_data = True

                try:
                    # Atualizar formulário com dados carregados
                    self._load_form_data_to_ui()

                    # Atualizar tabela com dados carregados
                    self._load_table_data_to_ui()

                    # Definir data atual no Page1 (para botão limpar)
                    self.page1.set_current_date(date)
                finally:
                    # CRÍTICO: Desativar flag após carregamento completo
                    self.page1._is_loading_data = False

                self.loading_progress.emit(80)

                # Aplicar estilo de salvo (verde)
                self._apply_saved_style()
                date_str = date.toString("dd/MM/yyyy")
                self.date_label.setText(f"✅ {date_str} - Carregado da BD")

                # Estado: Rascunho (sempre editável por enquanto)
                self._current_state = EstadoDocumento.RASCUNHO
                self.page1.setEnabled(True)

            else:
                # Dia não encontrado ou erro - criar novo dia
                logger.info(f"Dia não encontrado: {message}. Criando novo dia.")

                # Limpar formulário e tabela
                self._clear_form()
                self._clear_table()

                # Definir data atual no Page1 (para botão limpar)
                self.page1.set_current_date(date)

                # Aplicar estilo padrão
                self._apply_default_style()
                date_str = date.toString("dd/MM/yyyy")
                self.date_label.setText(f"📅 {date_str} - Novo dia")

                # Estado: Rascunho (novo dia)
                self._current_state = EstadoDocumento.RASCUNHO
                self.page1.setEnabled(True)

            # Resetar wizard para primeira página
            self.stack.setCurrentIndex(0)
            self.loading_progress.emit(100)

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            self.date_label.setText(
                "❌ Erro ao carregar dados da Base de Dados"
                )
        finally:
            self._is_loading = False
            self._set_ui_enabled(True)
            # Esconder barra de progresso imediatamente
            # (delay removido para evitar conflitos com event loop)
            self.loading_progress.emit(0)
