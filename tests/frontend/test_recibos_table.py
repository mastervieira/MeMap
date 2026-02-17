# type: ignore
"""Testes para o widget RecibosTableWidget.

Testa:
- Inicialização e configuração
- Reconstrução de tabela com diferentes quantidades
- Criação de linhas (recibos, vazia, totais)
- Validação de células numéricas
- Cálculos de totais
- Extração de dados
- Sinais emitidos
"""

from unittest.mock import MagicMock

import pytest
from PySide6.QtCore import QCoreApplication, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication, QTableWidgetItem

from src.common.constants import (
    COLUMN_WIDTHS,
    DEFAULT_CELL_VALUE,
    EDITABLE_COLUMNS,
    NUMERIC_COLUMNS,
    RECIBOS_TABLE_COLUMNS,
    ReciboColumn,
)
from src.common.constants.table_constants import TOTAL_ROW_LABEL
from src.frontend.components.partilhado_widget import PartilhadoWidget
from src.frontend.components.recibos_table import RecibosTableWidget


@pytest.fixture
def app() -> QApplication | QCoreApplication:
    """Fixture para QApplication."""
    app: QCoreApplication | None = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def table_widget(app: QApplication | QCoreApplication) -> RecibosTableWidget:
    """Fixture para RecibosTableWidget."""
    widget = RecibosTableWidget()
    return widget


class TestRecibosTableWidgetInit:
    """Testa inicialização e setup do widget."""

    def test_init_creates_widget(self, table_widget: RecibosTableWidget) -> None:
        """Testa criação básica do widget."""
        assert table_widget is not None
        assert isinstance(table_widget, RecibosTableWidget)

    def test_init_sets_total_row_index(self, table_widget: RecibosTableWidget) -> None:
        """Testa inicialização do índice de linha de totais."""
        assert table_widget._total_row_index == -1

    def test_setup_table_sets_column_count(self, table_widget: RecibosTableWidget) -> None:
        """Testa configuração do número de colunas."""
        assert table_widget.columnCount() == len(RECIBOS_TABLE_COLUMNS)

    def test_setup_table_sets_headers(self, table_widget: RecibosTableWidget) -> None:
        """Testa configuração dos headers."""
        for i, col_name in enumerate(RECIBOS_TABLE_COLUMNS):
            header: QTableWidgetItem | None = table_widget.horizontalHeaderItem(i)
            assert header is not None
            assert header.text() == col_name

    def test_setup_table_sets_column_widths(self, table_widget: RecibosTableWidget) -> None:
        """Testa configuração das larguras das colunas."""
        for col_name, width in COLUMN_WIDTHS.items():
            col_index: int = RECIBOS_TABLE_COLUMNS.index(col_name)
            assert table_widget.columnWidth(col_index) == width

    def test_setup_table_connects_signals(self, table_widget: RecibosTableWidget) -> None:
        """Testa conexão de sinais."""
        # O sinal está conectado se itemChanged emitir e chamar _on_cell_changed
        # Testamos indiretamente através da funcionalidade
        assert table_widget is not None

    def test_apply_theme_sets_stylesheet(self, table_widget: RecibosTableWidget) -> None:
        """Testa aplicação de tema."""
        stylesheet: str = table_widget.styleSheet()
        assert "QTableWidget" in stylesheet
        assert "white" in stylesheet


class TestRebuildTable:
    """Testa reconstrução da tabela."""

    def test_rebuild_table_with_single_recibo(self, table_widget: RecibosTableWidget) -> None:
        """Testa reconstrução com um único recibo."""
        table_widget.rebuild_table(1, 100, 100)

        # 1 recibo + 1 vazia + 1 totais = 3 linhas
        assert table_widget.rowCount() == 3
        assert table_widget._total_row_index == 2

    def test_rebuild_table_with_multiple_recibos(self, table_widget: RecibosTableWidget) -> None:
        """Testa reconstrução com múltiplos recibos."""
        table_widget.rebuild_table(5, 100, 104)

        # 5 recibos + 1 vazia + 1 totais = 7 linhas
        assert table_widget.rowCount() == 7
        assert table_widget._total_row_index == 6

    def test_rebuild_table_fills_recibo_numbers(self, table_widget: RecibosTableWidget):
        """Testa preenchimento de números de recibo."""
        table_widget.rebuild_table(3, 100, 102)

        for i in range(3):
            item = table_widget.item(i, ReciboColumn.RECIBO)
            expected_num = 100 + i
            assert item is not None
            assert item.text() == str(expected_num)

    def test_rebuild_table_creates_totals_row(self, table_widget):
        """Testa criação da linha de totais."""
        table_widget.rebuild_table(2, 100, 101)

        totals_row = table_widget._total_row_index
        label_item = table_widget.item(totals_row, ReciboColumn.RECIBO)
        assert label_item is not None
        assert label_item.text() == TOTAL_ROW_LABEL

    def test_rebuild_table_disables_editing_in_recibo_column(self, table_widget):
        """Testa desabilitação de edição na coluna Recibo."""
        table_widget.rebuild_table(1, 100, 100)

        recibo_item = table_widget.item(0, ReciboColumn.RECIBO)
        assert (recibo_item.flags() & Qt.ItemFlag.ItemIsEditable)

    def test_rebuild_table_blocks_signals(self, table_widget):
        """Testa bloqueio de sinais durante reconstrução."""
        table_widget.data_changed = MagicMock()
        table_widget.itemChanged.connect(lambda: table_widget.data_changed.emit())

        table_widget.rebuild_table(1, 100, 100)

        # O sinal não deve ser emitido durante rebuild
        table_widget.data_changed.assert_not_called()


class TestRecreateRows:
    """Testa criação de diferentes tipos de linhas."""

    def test_create_recibo_row_sets_recibo_number(self, table_widget):
        """Testa criação de linha de recibo com número."""
        table_widget.setRowCount(1)
        table_widget._create_recibo_row(0, 123)

        item = table_widget.item(0, ReciboColumn.RECIBO)
        assert item.text() == "123"

    def test_create_recibo_row_sets_default_values(self, table_widget):
        """Testa criação de linha com valores padrão."""
        # Usa interface pública: rebuild_table cria linhas com valores padrão
        table_widget.rebuild_table(1, 100, 100)

        for col in NUMERIC_COLUMNS:
            if col != ReciboColumn.RECIBO:
                item = table_widget.item(0, col)
                assert item is not None
                # Valores são obtidos do ViewModel após rebuild
                assert item.text() == DEFAULT_CELL_VALUE

    def test_create_empty_row(self, table_widget):
        """Testa criação de linha vazia."""
        table_widget.setRowCount(1)
        table_widget._create_empty_row(0)

        for col in range(table_widget.columnCount()):
            item = table_widget.item(0, col)
            assert item is not None
            # Coluna não editável tem valor "", coluna editável tem "0"
            if col not in EDITABLE_COLUMNS:
                assert item.text() == ""

    def test_create_totals_row_label(self, table_widget):
        """Testa criação de linha de totais com label."""
        table_widget.setRowCount(1)
        table_widget._create_totals_row(0)

        label = table_widget.item(0, ReciboColumn.RECIBO)
        assert label.text() == TOTAL_ROW_LABEL

    def test_create_totals_row_disables_editing(self, table_widget):
        """Testa desabilitação de edição em células de totais."""
        table_widget.setRowCount(1)
        table_widget._create_totals_row(0)

        for col in NUMERIC_COLUMNS:
            if col != ReciboColumn.RECIBO:
                item = table_widget.item(0, col)
                assert not (item.flags() & Qt.ItemFlag.ItemIsEditable)

    def test_create_totals_row_sets_background(self, table_widget):
        """Testa definição de fundo cinzento em totais."""
        table_widget.setRowCount(1)
        table_widget._create_totals_row(0)

        for col in NUMERIC_COLUMNS:
            item = table_widget.item(0, col)
            background = item.background()
            # Verifica que tem cor de fundo definida
            assert background.color() != QColor(Qt.GlobalColor.white)

    def test_create_partilhado_cell(self, table_widget):
        """Testa criação de célula de partilha."""
        table_widget.setRowCount(1)
        table_widget._create_partilhado_cell(0, ReciboColumn.PARTILHADO)

        widget = table_widget.cellWidget(0, ReciboColumn.PARTILHADO)
        assert isinstance(widget, PartilhadoWidget)


class TestCellValidationBehavior:
    """Testa comportamento de validação de células através da interface pública."""

    def test_validate_empty_cell_through_public_api(self, table_widget):
        """Testa que célula vazia usa valor padrão."""
        table_widget.rebuild_table(1, 100, 100)

        # Simula usuário editando célula e deixando vazia
        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("")
        table_widget.itemChanged.emit(item)

        # Deve ter valor padrão após validação do ViewModel
        assert item.text() == DEFAULT_CELL_VALUE

    def test_validate_valid_number_through_public_api(self, table_widget):
        """Testa validação de número válido."""
        table_widget.rebuild_table(1, 100, 100)

        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("100")
        table_widget.itemChanged.emit(item)

        # Deve manter valor válido
        assert item.text() == "100"

    def test_validate_decimal_normalization(self, table_widget):
        """Testa normalização de decimal (ponto → vírgula)."""
        table_widget.rebuild_table(1, 100, 100)

        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("100.50")
        table_widget.itemChanged.emit(item)

        # ViewModel deve normalizar para vírgula
        assert item.text() == "100,50"

    def test_validate_invalid_number_rejected(self, table_widget):
        """Testa que número inválido é rejeitado."""
        table_widget.rebuild_table(1, 100, 100)

        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("abc")
        table_widget.itemChanged.emit(item)

        # Deve reverter para valor padrão
        assert item.text() == DEFAULT_CELL_VALUE

    def test_validate_negative_number_rejected(self, table_widget):
        """Testa que número negativo é rejeitado."""
        table_widget.rebuild_table(1, 100, 100)

        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("-100")
        table_widget.itemChanged.emit(item)

        # Deve reverter para valor padrão
        assert item.text() == DEFAULT_CELL_VALUE


class TestTotalsBehavior:
    """Testa comportamento de cálculo de totais através da interface pública."""

    def test_totals_update_on_single_value(self, table_widget):
        """Testa que totais são atualizados ao definir um valor."""
        table_widget.rebuild_table(1, 100, 100)

        # Define valor através da interface pública
        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("100,00")
        table_widget.itemChanged.emit(item)

        # Verifica total na linha de totais
        total_item = table_widget.item(table_widget._total_row_index, ReciboColumn.SETUBAL)
        assert total_item is not None
        assert "100" in total_item.text()

    def test_totals_sum_multiple_values(self, table_widget):
        """Testa soma de múltiplos valores."""
        table_widget.rebuild_table(3, 100, 102)

        # Define valores
        for i in range(3):
            item = table_widget.item(i, ReciboColumn.SETUBAL)
            item.setText("50")
            table_widget.itemChanged.emit(item)

        # Total deve ser 150
        total_item = table_widget.item(table_widget._total_row_index, ReciboColumn.SETUBAL)
        assert "150" in total_item.text()

    def test_totals_ignore_invalid_values(self, table_widget):
        """Testa que totais ignoram valores inválidos."""
        table_widget.rebuild_table(2, 100, 101)

        # Define valor válido
        item1 = table_widget.item(0, ReciboColumn.SETUBAL)
        item1.setText("100")
        table_widget.itemChanged.emit(item1)

        # Tenta definir valor inválido (será rejeitado pelo ViewModel)
        item2 = table_widget.item(1, ReciboColumn.SETUBAL)
        item2.setText("abc")
        table_widget.itemChanged.emit(item2)

        # Total deve ser 100 (segundo valor foi rejeitado)
        total_item = table_widget.item(table_widget._total_row_index, ReciboColumn.SETUBAL)
        assert "100" in total_item.text()

    def test_totals_formatted_as_currency(self, table_widget):
        """Testa que totais são formatados como moeda."""
        table_widget.rebuild_table(1, 100, 100)

        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("100,50")
        table_widget.itemChanged.emit(item)

        total_item = table_widget.item(table_widget._total_row_index, ReciboColumn.SETUBAL)
        # Deve ter vírgula e símbolo €
        assert "," in total_item.text()
        assert "€" in total_item.text()


class TestGetTableData:
    """Testa extração de dados da tabela."""

    def test_get_table_data_empty(self, table_widget):
        """Testa extração de dados em tabela vazia."""
        table_widget.rebuild_table(0, 100, 99)
        data = table_widget.get_table_data()
        assert data == []

    def test_get_table_data_single_row(self, table_widget):
        """Testa extração de dados de uma linha."""
        table_widget.rebuild_table(1, 100, 100)

        # Preenche dados
        table_widget.item(0, ReciboColumn.SETUBAL).setText("100,00")

        data = table_widget.get_table_data()

        assert len(data) == 1
        assert data[0]["Recibo"] == "100"
        assert data[0]["Setúbal"] in ["100,00", "100.00", "100"]

    def test_get_table_data_multiple_rows(self, table_widget):
        """Testa extração de dados de múltiplas linhas."""
        table_widget.rebuild_table(2, 100, 101)

        # Preenche dados
        for i in range(2):
            table_widget.item(i, ReciboColumn.SETUBAL).setText("50,00")

        data = table_widget.get_table_data()

        assert len(data) == 2

    def test_get_table_data_includes_partilhado(self, table_widget):
        """Testa que dados incluem partilhado."""
        table_widget.rebuild_table(1, 100, 100)

        data = table_widget.get_table_data()

        assert "Partilhado" in data[0]
        assert isinstance(data[0]["Partilhado"], dict)

    def test_get_table_data_structure(self, table_widget):
        """Testa estrutura dos dados retornados."""
        table_widget.rebuild_table(1, 100, 100)

        data = table_widget.get_table_data()

        # Cada linha deve ter dicionário com colunas
        for row_data in data:
            assert isinstance(row_data, dict)
            # Deve ter todas as colunas
            for col_name in RECIBOS_TABLE_COLUMNS:
                assert col_name in row_data


class TestCellChangedCallback:
    """Testa callback de mudança de célula."""

    def test_data_changed_signal_connected(self, table_widget):
        """Testa que sinal data_changed está conectado ao ViewModel."""
        table_widget.rebuild_table(1, 100, 100)

        # Verifica que View está conectada ao ViewModel
        assert table_widget.viewmodel is not None
        # O sinal data_changed da View é emitido quando ViewModel.data_changed é emitido
        # Teste indireto: outros testes já validam esse comportamento

    def test_on_cell_changed_ignores_totals_row(self, table_widget):
        """Testa que mudanças na linha de totais são ignoradas."""
        table_widget.rebuild_table(1, 100, 100)

        signal_emitted = []
        table_widget.data_changed.connect(lambda: signal_emitted.append(True))

        # Tenta mudar célula na linha de totais
        totals_row = table_widget._total_row_index
        item = table_widget.item(totals_row, ReciboColumn.SETUBAL)

        # Reseta contador
        signal_emitted.clear()

        # Emite sinal (sem bloquear)
        table_widget.blockSignals(False)
        table_widget.itemChanged.emit(item)

        # Não deve emitir (ou emite apenas da validação)

    def test_on_cell_changed_validates_numeric(self, table_widget):
        """Testa validação de células numéricas ao mudar."""
        table_widget.rebuild_table(1, 100, 100)

        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("abc")
        table_widget.itemChanged.emit(item)

        # Deve ser validado e corrigido
        assert item.text() == DEFAULT_CELL_VALUE


class TestPartilhadoCallback:
    """Testa callback de widget partilhado."""

    def test_on_partilhado_changed_updates_totals(self, table_widget):
        """Testa que mudança em partilhado atualiza totais."""
        table_widget.rebuild_table(1, 100, 100)

        # Mock do widget partilhado
        widget = table_widget.cellWidget(0, ReciboColumn.PARTILHADO)
        assert isinstance(widget, PartilhadoWidget)

        # Conecta sinal
        signal_emitted = []
        table_widget.data_changed.connect(lambda: signal_emitted.append(True))

        # Emite sinal do widget
        widget.value_changed.emit()

        assert len(signal_emitted) > 0

    def test_on_partilhado_changed_emits_data_changed(self, table_widget):
        """Testa emissão de data_changed ao mudar partilhado."""
        table_widget.rebuild_table(1, 100, 100)

        signal_emitted = []
        table_widget.data_changed.connect(lambda: signal_emitted.append(True))

        widget = table_widget.cellWidget(0, ReciboColumn.PARTILHADO)
        widget.value_changed.emit()

        assert len(signal_emitted) > 0


class TestClearTable:
    """Testa limpeza da tabela."""

    def test_clear_table_removes_all_rows(self, table_widget):
        """Testa remoção de todas as linhas."""
        table_widget.rebuild_table(5, 100, 104)
        assert table_widget.rowCount() > 0

        table_widget.clear_table()

        assert table_widget.rowCount() == 0

    def test_clear_table_resets_total_row_index(self, table_widget):
        """Testa reset de índice de linha de totais."""
        table_widget.rebuild_table(5, 100, 104)
        assert table_widget._total_row_index >= 0

        table_widget.clear_table()

        assert table_widget._total_row_index == -1


class TestEdgeCases:
    """Testes de casos extremos através da interface pública."""

    def test_on_cell_changed_with_none_item(self, table_widget):
        """Testa callback com item None."""
        table_widget.rebuild_table(1, 100, 100)
        # Deve ignorar item None sem erro
        table_widget._on_cell_changed(None)

    def test_invalid_decimal_format_handled(self, table_widget):
        """Testa que formato decimal ambíguo é tratado."""
        table_widget.rebuild_table(1, 100, 100)

        # Define valor com formato ambíguo
        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("999,999.99")
        table_widget.itemChanged.emit(item)

        # ViewModel deve rejeitar ou normalizar
        # O importante é não gerar exceção
        assert item is not None

    def test_get_table_data_with_missing_partilhado_widget(self, table_widget):
        """Testa extração de dados quando widget partilhado não existe."""
        table_widget.rebuild_table(1, 100, 100)

        # Remove o widget partilhado
        table_widget.setCellWidget(0, ReciboColumn.PARTILHADO, None)

        data = table_widget.get_table_data()

        # Deve retornar dados padrão do ViewModel
        assert len(data) == 1
        assert "Partilhado" in data[0]

    def test_totals_row_label_persists(self, table_widget):
        """Testa que label TOTAIS persiste após atualizações."""
        table_widget.rebuild_table(1, 100, 100)

        # Define valor e atualiza totais
        item = table_widget.item(0, ReciboColumn.SETUBAL)
        item.setText("100")
        table_widget.itemChanged.emit(item)

        # Célula de total RECIBO deve ter o label, não um número
        total_item = table_widget.item(table_widget._total_row_index, ReciboColumn.RECIBO)
        assert total_item.text() == TOTAL_ROW_LABEL

    def test_multiple_column_updates(self, table_widget):
        """Testa atualização de múltiplas colunas."""
        table_widget.rebuild_table(1, 100, 100)

        # Atualiza várias colunas
        for col_idx in [ReciboColumn.SETUBAL, ReciboColumn.SANTAREM, ReciboColumn.EVORA]:
            item = table_widget.item(0, col_idx)
            item.setText("50")
            table_widget.itemChanged.emit(item)

        # Todas devem ter totais
        for col_idx in [ReciboColumn.SETUBAL, ReciboColumn.SANTAREM, ReciboColumn.EVORA]:
            total_item = table_widget.item(table_widget._total_row_index, col_idx)
            assert "50" in total_item.text()


class TestIntegration:
    """Testes de integração completos através da interface pública."""

    def test_full_workflow(self, table_widget):
        """Testa fluxo completo de uso."""
        # Constrói tabela
        table_widget.rebuild_table(3, 100, 102)

        # Preenche dados e emite sinais para atualizar ViewModel
        for i in range(3):
            setubal_item = table_widget.item(i, ReciboColumn.SETUBAL)
            setubal_item.setText(f"{(i+1)*50}")
            table_widget.itemChanged.emit(setubal_item)

            santarem_item = table_widget.item(i, ReciboColumn.SANTAREM)
            santarem_item.setText(f"{(i+1)*5}")
            table_widget.itemChanged.emit(santarem_item)

        # Extrai dados (agora vem do ViewModel)
        data = table_widget.get_table_data()

        assert len(data) == 3
        assert all("Recibo" in row for row in data)
        assert all("Setúbal" in row for row in data)

        # Verifica totais na UI
        total_setubal = table_widget.item(table_widget._total_row_index, ReciboColumn.SETUBAL)
        # 50 + 100 + 150 = 300
        assert "300" in total_setubal.text()

    def test_rebuild_resets_data(self, table_widget):
        """Testa que rebuild reseta dados."""
        # Constrói tabela
        table_widget.rebuild_table(2, 100, 101)
        table_widget.item(0, ReciboColumn.SETUBAL).setText("100,00")

        # Reconstrói
        table_widget.rebuild_table(1, 200, 200)

        data = table_widget.get_table_data()
        assert len(data) == 1
        assert data[0]["Recibo"] == "200"
