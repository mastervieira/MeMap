"""
Widget de tabela de recibos para o formulário guiado do MeMap Pro.
Implementa tabela tipo Excel com validação, checkboxes e totais automáticos.

REFATORAÇÃO MVVM:
- View apenas gerencia UI e renderização
- ViewModel gerencia lógica de negócio e dados
"""

import logging

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QFont, QKeyEvent
from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QWidget,
    QMessageBox
)
from src.common.normalizers.decimal_normalizer import decimal_to_float
from src.common.constants import (
    COLUMN_WIDTHS,
    EDITABLE_COLUMNS,
    NUMERIC_COLUMNS,
    RECIBOS_TABLE_COLUMNS,
    ReciboColumn,
)
from src.common.constants.table_constants import ROW_HEIGHT, TOTAL_ROW_LABEL
from src.frontend.components.notifications import NotificationManager
from src.frontend.components.partilhado_widget import PartilhadoWidget
from src.frontend.viewmodels.recibos_table_viewmodel import RecibosTableViewModel

logger: logging.Logger = logging.getLogger(__name__)


class RecibosTableWidget(QTableWidget):
    """Tabela interativa tipo Excel para entrada de dados de recibos.

    Features:
    - Criação dinâmica de linhas baseada em quantidade de recibos
    - Preenchimento automático da coluna 'Recibo' com sequência
    - Checkbox na coluna 'Partilhado'
    - Validação de campos numéricos (delegada ao ViewModel)
    - Linha de totais automáticos (última linha)
    - Cálculos em tempo real (delegados ao ViewModel)
    """

    # Sinal emitido quando dados da tabela mudam
    data_changed = Signal()

    def __init__(
        self,
        viewmodel: RecibosTableViewModel | None = None,
        parent: QWidget | None = None
    ) -> None:
        """Inicializa a tabela com ViewModel.

        Args:
            viewmodel: ViewModel para gerenciar dados (cria um padrão se None)
            parent: Widget pai
        """
        super().__init__(parent)
        self._total_row_index: int = -1
        self._servico_interno_row_index: int = -1  # FASE 4: índice da linha de serviço interno

        # Injeta ou cria ViewModel
        self._viewmodel: RecibosTableViewModel = viewmodel if viewmodel \
        else RecibosTableViewModel()

        # Conecta sinais do ViewModel → View
        self._viewmodel.data_changed.connect(self._on_viewmodel_data_changed)
        self._viewmodel.totals_updated.connect(self._update_totals_display)
        self._viewmodel.table_rebuilt.connect(self._on_table_rebuilt)
        self._viewmodel.servico_interno_changed.connect(
            self._on_servico_interno_changed)
        self._viewmodel.recibo_sequence_updated.connect(
            self._update_recibo_cells)
        self._viewmodel.row_added.connect(self._on_row_added)
        self._viewmodel.recibo_validation_changed.connect(
            self._on_recibo_validation_changed)

        # Aumenta fonte em 15%
        current_font: QFont = self.font()
        new_size = int(current_font.pointSize() * 1.15)
        new_font = QFont(current_font.family(), new_size)
        self.setFont(new_font)

        self._setup_table()

    def _setup_table(self) -> None:
        """Configura a estrutura básica da tabela."""
        # Define número de colunas
        self.setColumnCount(len(RECIBOS_TABLE_COLUMNS))

        # Define cabeçalhos
        self.setHorizontalHeaderLabels(RECIBOS_TABLE_COLUMNS)

        # Configurações visuais
        self.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )

        # Ajusta larguras das colunas
        for col_name, width in COLUMN_WIDTHS.items():
            col_index: int = RECIBOS_TABLE_COLUMNS.index(col_name)
            self.setColumnWidth(col_index, width)

        # Ajusta altura das linhas
        self.verticalHeader().setDefaultSectionSize(ROW_HEIGHT)

        # Header ajustável
        header: QHeaderView = self.horizontalHeader()
        if header:
            header.setStretchLastSection(True)

        # Conecta sinal de mudança de célula
        self.itemChanged.connect(self._on_cell_changed)

        # Aplica tema inicial
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Aplica o tema atual à tabela."""
        self.setStyleSheet("""
            QTableWidget {
                background-color: white;
                color: black;
                gridline-color: #e0e0e0;
                border: 1px solid #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
                background-color: white;
                color: black;
            }
            QTableWidget::item:selected {
                background-color: white;
                color: black;
            }
            QHeaderView::section {
                background-color: white;
                color: black;
                padding: 5px;
                border: 1px solid #e0e0e0;
                font-weight: bold;
            }
        """)

    def rebuild_table(
        self,
        quantidade: int,
        recibo_inicio: int,
        recibo_fim: int
    ) -> None:
        """Reconstrói a tabela com novo conjunto de recibos.

        Args:
            quantidade: Número de recibos
            recibo_inicio: Número do primeiro recibo
            recibo_fim: Número do último recibo
        """
        # Delega ao ViewModel para reconstruir estrutura de dados
        self._viewmodel.rebuild_data(quantidade, recibo_inicio, recibo_fim)

        # A UI será atualizada pelo sinal table_rebuilt

    def _on_table_rebuilt(
            self,
            quantidade: int,
            recibo_inicio: int,
            recibo_fim: int
            ) -> None:
        """Callback quando ViewModel reconstrói dados.

        FASE 4 (CORRIGIDO): Respeita estado de Serviço Interno.
        Se Serviço Interno está ativo, mantém linha de SI no topo.
        """
        # Bloqueia sinais durante reconstrução
        self.blockSignals(True)

        # Verificar se Serviço Interno está ativo
        servico_interno_ativo: bool = self._viewmodel.is_servico_interno()

        # Limpa tabela
        self.setRowCount(0)

        row_offset = 0  # Offset para ajustar índices

        # Se Serviço Interno ativo, adicionar linha de SI primeiro
        if servico_interno_ativo:
            self.insertRow(0)
            self._servico_interno_row_index = 0

            # Primeira coluna: "🔧 SERVIÇO INTERNO" como texto real
            servico_item = QTableWidgetItem("🔧 SERVIÇO INTERNO")
            servico_item.setBackground(QColor("#ffe082"))
            servico_item.setForeground(QColor("#F57C00"))
            servico_item.setFlags(
                servico_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            font: QFont = servico_item.font()
            font.setBold(True)
            font.setPointSize(10)
            servico_item.setFont(font)
            servico_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(0, ReciboColumn.RECIBO, servico_item)

            # Fazer span da primeira coluna até antes de Km
            self.setSpan(0, ReciboColumn.RECIBO, 1, ReciboColumn.KM)

            # Coluna Km: editável
            km_item = QTableWidgetItem("0")
            km_item.setBackground(QColor("#ffe082"))
            km_item.setFlags(km_item.flags() | Qt.ItemFlag.ItemIsEditable)
            km_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.setItem(0, ReciboColumn.KM, km_item)

            # Coluna Nº IPs: não editável
            ips_item = QTableWidgetItem("")
            ips_item.setBackground(QColor("#ffe082"))
            ips_item.setFlags(ips_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(0, ReciboColumn.NUM_IPS, ips_item)

            # Coluna Partilhado: não editável
            partilhado_item = QTableWidgetItem("")
            partilhado_item.setBackground(QColor("#ffe082"))
            partilhado_item.setFlags(
                partilhado_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(0, ReciboColumn.PARTILHADO, partilhado_item)

            # Coluna Ações: não editável (serviço interno não pode ser eliminado)
            acoes_item = QTableWidgetItem("")
            acoes_item.setBackground(QColor("#ffe082"))
            acoes_item.setFlags(acoes_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self.setItem(0, ReciboColumn.ACOES, acoes_item)

            row_offset = 1  # Linhas de dados começam em 1

        # Calcula número total de linhas
        # recibos + linha vazia + linha totais (+ linha SI se ativa)
        total_rows: int = row_offset + quantidade + 2
        self.setRowCount(total_rows)

        # Preenche linhas de recibos
        # CORRIGIDO: Ler recibos do ViewModel em vez de calcular sequência
        # (para suportar duplicados e gaps)
        for i in range(quantidade):
            row_index: int = row_offset + i
            # Obter número do recibo do ViewModel (pode ser duplicado)
            recibo_data: dict[str, str] | None = self._viewmodel.get_data()[i] \
                if i < len(self._viewmodel.get_data()) else None
            recibo_num: int = int(recibo_data.get("Recibo", recibo_inicio + i)) \
                if recibo_data else (recibo_inicio + i)
            self._create_recibo_row(row_index, recibo_num)

            # Preencher dados das células do ViewModel
            if recibo_data:
                for col_idx, col_name in enumerate(RECIBOS_TABLE_COLUMNS):
                    if col_name == "Recibo":
                        continue  # Já preenchido em _create_recibo_row
                    elif col_name == "Partilhado":
                        # Partilhado tem widget especial, será preenchido depois
                        continue
                    elif col_name in recibo_data:
                        value: str = recibo_data[col_name]
                        item: QTableWidgetItem | None = self.item(
                            row_index, col_idx)
                        if item:
                            item.setText(str(value))

        # Linha vazia (após recibos)
        empty_row_index: int = row_offset + quantidade
        self._create_empty_row(empty_row_index)

        # Linha de totais (última)
        self._total_row_index = row_offset + quantidade + 1
        self._create_totals_row(self._total_row_index)

        # Reativa sinais
        self.blockSignals(False)

        # BUGFIX: Atualizar totais após criar estrutura da tabela
        # Garante que valores dos totais são exibidos corretamente
        totals: dict[str, float] = self._viewmodel.get_totals()
        if totals:
            self._update_totals_display(totals)

    def _create_recibo_row(self, row_index: int, recibo_num: int) -> None:
        """Cria uma linha de recibo com valores iniciais.

        Args:
            row_index: Índice da linha na tabela
            recibo_num: Número do recibo
        """
        # FASE 5: Coluna Recibo EDITÁVEL (removido flag ItemIsEditable)
        recibo_item = QTableWidgetItem(str(recibo_num))
        recibo_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row_index, ReciboColumn.RECIBO, recibo_item)

        # Colunas numéricas editáveis - obtém valores do ViewModel
        for col in NUMERIC_COLUMNS:
            if col != ReciboColumn.RECIBO:
                col_name: str = RECIBOS_TABLE_COLUMNS[col]
                value: str = self._viewmodel.get_cell_value(row_index, col_name)
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_index, col, item)

        # Coluna Partilhado (widget customizado)
        self._create_partilhado_cell(row_index, ReciboColumn.PARTILHADO)

        # FEATURE 2: Coluna Ações (botão eliminar)
        self._create_delete_button(row_index, ReciboColumn.ACOES)

    def _create_empty_row(self, row_index: int) -> None:
        """Cria linha vazia."""
        for col in range(self.columnCount()):
            item = QTableWidgetItem("")
            # Linha vazia não tem botão de ações
            if col not in EDITABLE_COLUMNS or col == ReciboColumn.ACOES:
                item.setFlags(
                    item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
            self.setItem(row_index, col, item)

    def _create_totals_row(self, row_index: int) -> None:
        """Cria linha de totais.

        Args:
            row_index: Índice da linha de totais
        """
        # Label "TOTAIS"
        label_item = QTableWidgetItem(TOTAL_ROW_LABEL)
        label_item.setFlags(
            label_item.flags() & ~Qt.ItemFlag.ItemIsEditable
        )
        label_item.setBackground(Qt.GlobalColor.lightGray)
        self.setItem(row_index, ReciboColumn.RECIBO, label_item)

        # Células de totais (não editáveis, fundo cinzento claro)
        for col in NUMERIC_COLUMNS:
            if col != ReciboColumn.RECIBO:
                total_item = QTableWidgetItem("0,00 €")
                total_item.setFlags(
                    total_item.flags() & ~Qt.ItemFlag.ItemIsEditable
                )
                total_item.setBackground(Qt.GlobalColor.lightGray)
                total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.setItem(row_index, col, total_item)

        # Coluna Partilhado: sem valor (apenas indicador)
        partilhado_total_item = QTableWidgetItem("---")
        partilhado_total_item.setFlags(
            partilhado_total_item.flags() & ~Qt.ItemFlag.ItemIsEditable
        )
        partilhado_total_item.setBackground(Qt.GlobalColor.lightGray)
        partilhado_total_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(row_index, ReciboColumn.PARTILHADO, partilhado_total_item)

        # Coluna Ações: sem valor (linha de totais não tem ações)
        acoes_total_item = QTableWidgetItem("")
        acoes_total_item.setFlags(
            acoes_total_item.flags() & ~Qt.ItemFlag.ItemIsEditable
        )
        acoes_total_item.setBackground(Qt.GlobalColor.lightGray)
        self.setItem(row_index, ReciboColumn.ACOES, acoes_total_item)

    def _create_partilhado_cell(self, row: int, col: int) -> None:
        """Cria célula com widget de partilha customizado.

        Args:
            row: Índice da linha
            col: Índice da coluna
        """
        partilhado_widget = PartilhadoWidget()
        partilhado_widget.value_changed.connect(
            lambda: self._on_partilhado_changed(row)
        )
        self.setCellWidget(row, col, partilhado_widget)

    def _create_delete_button(self, row: int, col: int) -> None:
        """Cria botão de eliminar linha.

        FEATURE 2: Adiciona mini-botão com ícone 🗑️ para eliminar linha.

        Args:
            row: Índice da linha
            col: Índice da coluna
        """

        # Criar botão com ícone de lixo
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 30)
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                font-size: 16px;
                padding: 0;
            }
            QPushButton:hover {
                background-color: #ffebee;
                border-radius: 4px;
            }
            QPushButton:pressed {
                background-color: #ffcdd2;
            }
        """)
        delete_btn.setToolTip("Eliminar linha")
        delete_btn.clicked.connect(lambda: self._on_delete_row_clicked(row))

        # Centralizar botão na célula
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.addWidget(delete_btn)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setContentsMargins(0, 0, 0, 0)

        self.setCellWidget(row, col, container)

    def _on_partilhado_changed(self, row: int) -> None:
        """Callback quando widget de partilha muda.

        Args:
            row: Linha que mudou
        """
        # Obtém dados do widget
        widget: QWidget = self.cellWidget(row, ReciboColumn.PARTILHADO)
        if isinstance(widget, PartilhadoWidget):
            partilhado_data: dict[str, bool | str] = widget.get_data()
            # Atualiza ViewModel
            self._viewmodel.set_partilhado_data(row, partilhado_data)

    def _on_delete_row_clicked(self, row: int) -> None:
        """Callback quando botão de eliminar é clicado.

        FEATURE 2: Elimina linha da tabela e da BD.

        Args:
            row: Índice da linha na View
        """


        # Confirmar com usuário
        recibo_item: QTableWidgetItem | None = self.item(row, ReciboColumn.RECIBO)
        if not recibo_item:
            return

        recibo_num: str = recibo_item.text()

        reply: QMessageBox.StandardButton = QMessageBox.question(
            self,
            "Confirmar Eliminação",
            f"Tem certeza que deseja eliminar o recibo {recibo_num}?\n\nEsta ação é permanente.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        # Calcular índice de dados (ajustar para Serviço Interno se ativo)
        data_row: int = row
        if self._servico_interno_row_index >= 0:
            data_row = row - 1

        # Validar índice de dados
        if data_row < 0:
            logger.warning(f"Índice de dados inválido: {data_row}")
            return

        # Bloquear sinais durante eliminação
        self.blockSignals(True)

        # Eliminar do ViewModel (isso também emitirá signal row_deleted)
        success: bool = self._viewmodel.delete_row(data_row)

        if success:
            # Remover linha da View
            self.removeRow(row)

            # Ajustar índice da linha de totais
            if self._total_row_index > row:
                self._total_row_index -= 1

            logger.info(f"Linha {row} (Recibo {recibo_num}) eliminada com sucesso")
        else:
            logger.error(f"Falha ao eliminar linha {row} (Recibo {recibo_num})")
            NotificationManager.instance().error(
                f"Não foi possível eliminar o recibo {recibo_num}."
            )

        # Reativar sinais
        self.blockSignals(False)

        # Emitir signal de mudança de dados
        self.data_changed.emit()

    @Slot(QTableWidgetItem)
    def _on_cell_changed(self, item: QTableWidgetItem) -> None:
        """Callback quando uma célula é alterada.

        Delega validação e cálculos ao ViewModel.

        Args:
            item: Item da célula que mudou
        """
        if not item:
            return

        row: int = item.row()
        col: int = item.column()

        # Ignora mudanças na linha de totais e linha vazia
        if row == self._total_row_index or row == self._total_row_index - 1:
            return

        # Ignora mudanças na linha de Serviço Interno (exceto Km)
        if row == self._servico_interno_row_index and col != ReciboColumn.KM:
            return

        # Calcular índice de dados (ajustar para Serviço Interno se ativo)
        # Se Serviço Interno está ativo, dados começam na linha 1
        data_row: int = row
        if self._servico_interno_row_index >= 0:
            data_row = row - 1  # Ajustar para offset de Serviço Interno

        # Validar índice de dados
        if data_row < 0:
            return

        # Delega validação ao ViewModel
        # FASE 5: Incluir coluna Recibo para auto-incremento
        if col in NUMERIC_COLUMNS or col == ReciboColumn.RECIBO:
            col_name: str = RECIBOS_TABLE_COLUMNS[col]
            value: str = item.text()

            # Bloqueia sinais temporariamente para evitar loop
            self.blockSignals(True)

            try:
                # Valida através do ViewModel (usa data_row ajustado)
                accepted: bool = self._viewmodel.set_cell_value(
                    data_row, col_name, value)

                if accepted:
                    # Atualiza célula com valor normalizado do ViewModel
                    normalized_value: str = self._viewmodel.get_cell_value(
                        data_row, col_name)

                    # Verificar se o item ainda existe antes de atualizar
                    # (pode ter sido deletado durante reconstrução da tabela)
                    if item is not None and self.item(row, col) is item: # type: ignore
                        item.setText(normalized_value)
            except RuntimeError:
                # Item foi deletado durante processamento (esperado durante mudanças de dia)
                pass
            finally:
                self.blockSignals(False)

    def _on_viewmodel_data_changed(self) -> None:
        """Callback quando dados do ViewModel mudam.

        Emite sinal para notificar componentes externos.
        """
        self.data_changed.emit()

    def _update_totals_display(self, totals: dict[str, float]) -> None:
        """Atualiza exibição dos totais na linha de totais.

        Args:
            totals: Dicionário com totais calculados pelo ViewModel
        """
        # Se linha de totais não existe, criar
        if self._total_row_index < 0:
            # Verificar se há dados para criar linha de totais
            if self.rowCount() > 0:
                # Adicionar linha de totais no final
                self._total_row_index = self.rowCount()
                self.insertRow(self._total_row_index)
                self._create_totals_row(self._total_row_index)
                logger.debug(f"Linha de totais criada no índice {self._total_row_index}")
            else:
                return

        # Obtém totais formatados do ViewModel
        formatted_totals: dict[str, str] = self._viewmodel.get_formatted_totals()

        # Atualiza células de total
        for col_name, formatted_value in formatted_totals.items():
            col_index: int = RECIBOS_TABLE_COLUMNS.index(col_name)
            total_item: QTableWidgetItem | None = self.item(self._total_row_index, col_index)
            if total_item:
                total_item.setText(formatted_value)

    def get_table_data(self) -> list[dict[str, str | dict[str, str | bool]]]:
        """Extrai dados da tabela em formato estruturado.

        Delega ao ViewModel para obter dados consistentes.

        Returns:
            Lista de dicionários com dados de cada recibo
        """
        # Obtém dados do ViewModel
        return self._viewmodel.get_data()

    def clear_table(self) -> None:
        """Limpa toda a tabela."""
        self.setRowCount(0)
        self._total_row_index = -1
        self._viewmodel.clear_data()

    @property
    def viewmodel(self) -> RecibosTableViewModel:
        """Retorna o ViewModel associado."""
        return self._viewmodel

    # ==================== FASE 4: SERVIÇO INTERNO (CORRIGIDO) ====================

    def _on_servico_interno_changed(self, enabled: bool) -> None:
        """Callback quando modo Serviço Interno muda.

        FASE 4 (CORRIGIDO): Adiciona/remove linha extra abaixo do cabeçalho.

        Args:
            enabled: True se modo ativado, False se desativado
        """
        if enabled:
            self._add_servico_interno_row()
        else:
            self._remove_servico_interno_row()

    def _add_servico_interno_row(self) -> None:
        """Adiciona linha de Serviço Interno + linha vazia + totais.

        FASE 4 (CORRIGIDO V2): Insere "SERVIÇO INTERNO" como DADOS na tabela.
        - Linha 0: Serviço Interno (texto real nas células, apenas Km editável)
        - Linha 1: Vazia
        - Linha 2: Totais
        """
        # Bloqueia sinais
        self.blockSignals(True)

        # Limpar tabela primeiro
        self.setRowCount(0)

        # Adicionar 3 linhas: Serviço Interno + Vazia + Totais
        self.setRowCount(3)

        # === LINHA 0: SERVIÇO INTERNO ===
        self._servico_interno_row_index = 0

        # Primeira coluna: "🔧 SERVIÇO INTERNO" como texto real
        servico_item = QTableWidgetItem("🔧 SERVIÇO INTERNO")
        servico_item.setBackground(QColor("#ffe082"))  # Amarelo claro
        servico_item.setForeground(QColor("#F57C00"))  # Laranja
        servico_item.setFlags(servico_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        font = servico_item.font()
        font.setBold(True)
        font.setPointSize(10)
        servico_item.setFont(font)
        servico_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(0, ReciboColumn.RECIBO, servico_item)

        # Fazer span da primeira coluna até antes de Km (para texto ocupar múltiplas colunas)
        # Span: Recibo até Évora (colunas 0-4)
        self.setSpan(0, ReciboColumn.RECIBO, 1, ReciboColumn.KM)

        # Coluna Km: editável com valor inicial "0"
        km_item = QTableWidgetItem("0")
        km_item.setBackground(QColor("#ffe082"))
        km_item.setFlags(km_item.flags() | Qt.ItemFlag.ItemIsEditable)
        km_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setItem(0, ReciboColumn.KM, km_item)

        # Coluna Nº IPs: não editável, fundo amarelo
        ips_item = QTableWidgetItem("")
        ips_item.setBackground(QColor("#ffe082"))
        ips_item.setFlags(ips_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, ReciboColumn.NUM_IPS, ips_item)

        # Coluna Partilhado: não editável, fundo amarelo
        partilhado_item = QTableWidgetItem("")
        partilhado_item.setBackground(QColor("#ffe082"))
        partilhado_item.setFlags(partilhado_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, ReciboColumn.PARTILHADO, partilhado_item)

        # Coluna Ações: não editável, fundo amarelo (serviço interno não pode ser eliminado)
        acoes_item = QTableWidgetItem("")
        acoes_item.setBackground(QColor("#ffe082"))
        acoes_item.setFlags(acoes_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
        self.setItem(0, ReciboColumn.ACOES, acoes_item)

        # === LINHA 1: VAZIA ===
        self._create_empty_row(1)

        # === LINHA 2: TOTAIS ===
        self._total_row_index = 2
        self._create_totals_row(2)

        # Reativa sinais
        self.blockSignals(False)

        # BUGFIX: Atualizar totais após criar estrutura
        totals = self._viewmodel.get_totals()
        if totals:
            self._update_totals_display(totals)

        logger.info("Estrutura de Serviço Interno adicionada (3 linhas) com texto como dados")

    def _remove_servico_interno_row(self) -> None:
        """Remove estrutura de Serviço Interno (limpa tabela).

        FASE 4 (CORRIGIDO V2): Remove todas as linhas criadas pelo Serviço Interno.
        """
        if self._servico_interno_row_index < 0:
            return

        # Bloqueia sinais
        self.blockSignals(True)

        # Limpar tabela completamente (remove span também)
        self.clearSpans()
        self.setRowCount(0)
        self._servico_interno_row_index = -1
        self._total_row_index = -1

        # Reativa sinais
        self.blockSignals(False)

        logger.info("Estrutura de Serviço Interno removida")



    def get_servico_interno_km(self) -> float:
        """Retorna valor de Km da linha de Serviço Interno.

        FASE 4: Obtém valor digitado pelo usuário na coluna Km
        da linha de Serviço Interno.

        Returns:
            Valor de Km (0.0 se linha não existe ou valor inválido)
        """
        if self._servico_interno_row_index < 0:
            return 0.0

        km_item: QTableWidgetItem | None = self.item(
            self._servico_interno_row_index, ReciboColumn.KM)
        if not km_item:
            return 0.0

        try:
            return decimal_to_float(km_item.text())
        except (ValueError, AttributeError):
            return 0.0

    # ==================== FASE 5: RECIBOS EDITÁVEIS ====================

    def _update_recibo_cells(self, start_row: int, new_values: list[str]) -> None:
        """Atualiza células de Recibo após recálculo automático.

        Args:
            start_row: Linha inicial da atualização (índice do ViewModel)
            new_values: Lista de novos valores para as linhas subsequentes
        """
        self.blockSignals(True)

        # Ajustar índice se Serviço Interno está ativo
        # ViewModel envia índices sem offset, View precisa adicionar offset
        row_offset: int = 1 if self._servico_interno_row_index >= 0 else 0

        for i, value in enumerate(new_values):
            # Converter índice do ViewModel para índice da View
            view_row: int = start_row + i + row_offset
            if view_row < self.rowCount():
                item: QTableWidgetItem | None = self.item(view_row, ReciboColumn.RECIBO)
                if item:
                    item.setText(value)

        self.blockSignals(False)

    def _on_recibo_validation_changed(self, data_row: int, is_valid: bool) -> None:
        """Marca célula de recibo como vermelha se inválida (duplicado).

        Args:
            data_row: Índice da linha nos dados do ViewModel
            is_valid: True se recibo válido, False se duplicado
        """
        # Ajustar índice para View (considerar offset de Serviço Interno)
        row_offset: int = 1 if self._servico_interno_row_index >= 0 else 0
        view_row: int = data_row + row_offset

        if view_row >= self.rowCount():
            return

        item: QTableWidgetItem | None = self.item(view_row, ReciboColumn.RECIBO)
        if not item:
            return

        try:
            if is_valid:
                # Limpar marcação vermelha (restaurar cor padrão)
                item.setBackground(Qt.GlobalColor.white)
                item.setForeground(Qt.GlobalColor.black)
            else:
                # Marcar vermelho (recibo duplicado)
                item.setBackground(QColor("#ffcccc"))  # Vermelho claro
                item.setForeground(QColor("#cc0000"))  # Vermelho escuro
                item.setToolTip("⚠️ Recibo duplicado!")

            logger.debug(f"Recibo linha {view_row}: {'válido' if is_valid else 'DUPLICADO'}")
        except RuntimeError:
            # Item foi deletado durante processamento (esperado durante mudanças de dia)
            pass

    # ==================== FASE 6: ADICIONAR LINHAS ====================

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """Captura eventos de teclado.

        FASE 6: Adiciona linha quando tecla "+" é pressionada.

        Args:
            event: Evento de teclado
        """
        if event.key() == Qt.Key.Key_Plus:
            # Adicionar linha
            self._viewmodel.add_row()
            event.accept()
        else:
            super().keyPressEvent(event)

    def _on_row_added(self, row_index: int, row_data: dict[str, str]) -> None:
        """Callback quando linha é adicionada pelo ViewModel.

        FASE 6 (CORRIGIDO): Insere ANTES da linha vazia (não antes dos totais).

        Args:
            row_index: Índice da nova linha nos dados
            row_data: Dicionário com dados da nova linha
        """
        # Bloqueia sinais durante adição
        self.blockSignals(True)

        # Inserir nova linha ANTES da linha vazia
        # Estrutura: [...dados...] [vazia] [totais]
        # Linha vazia está sempre em _total_row_index - 1
        # Queremos inserir ANTES da vazia, então: _total_row_index - 1
        insert_position: int = (
            self._total_row_index - 1) if self._total_row_index >= 0 else self.rowCount()

        self.insertRow(insert_position)

        # Criar células para a nova linha
        recibo_num = int(row_data["Recibo"])
        self._create_recibo_row(insert_position, recibo_num)

        # Ajustar índice da linha de totais (agora está uma posição abaixo)
        # Linha vazia também se move automaticamente
        if self._total_row_index >= 0:
            self._total_row_index += 1

        # Reativa sinais
        self.blockSignals(False)

        logger.info(f"Linha {insert_position} adicionada na UI (Recibo {recibo_num})")
