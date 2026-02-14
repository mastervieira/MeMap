"""Testes para RecibosTableViewModel."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QApplication

from src.frontend.viewmodels.recibos_table_viewmodel import RecibosTableViewModel


@pytest.fixture(scope="session")
def qapp():
    """Fixture para QApplication necessário para QObject/Signal."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture
def viewmodel(qapp):
    """Fixture para RecibosTableViewModel."""
    return RecibosTableViewModel()


class TestViewModelInstantiation:
    """Testes de instanciação do ViewModel."""

    def test_init_creates_viewmodel(self, viewmodel):
        """Testa que ViewModel pode ser instanciado."""
        assert viewmodel is not None
        assert isinstance(viewmodel, RecibosTableViewModel)

    def test_init_sets_initial_state(self, viewmodel):
        """Testa que estado inicial está correto."""
        assert viewmodel.is_empty is True
        assert viewmodel.row_count == 0
        assert viewmodel.get_totals() == {}


class TestRebuildData:
    """Testes de reconstrução de dados."""

    def test_rebuild_data_single_recibo(self, viewmodel):
        """Testa reconstrução com um recibo."""
        viewmodel.rebuild_data(1, 100, 100)

        assert viewmodel.row_count == 1
        assert viewmodel.is_empty is False
        assert viewmodel.get_cell_value(0, "Recibo") == "100"

    def test_rebuild_data_multiple_recibos(self, viewmodel):
        """Testa reconstrução com múltiplos recibos."""
        viewmodel.rebuild_data(5, 200, 204)

        assert viewmodel.row_count == 5
        for i in range(5):
            expected_num = 200 + i
            assert viewmodel.get_cell_value(i, "Recibo") == str(expected_num)

    def test_rebuild_data_initializes_numeric_columns(self, viewmodel):
        """Testa que colunas numéricas são inicializadas com valor padrão."""
        viewmodel.rebuild_data(1, 100, 100)

        # Colunas numéricas devem ter valor padrão "0"
        assert viewmodel.get_cell_value(0, "Setúbal") == "0"
        assert viewmodel.get_cell_value(0, "Santarém") == "0"
        assert viewmodel.get_cell_value(0, "Évora") == "0"

    def test_rebuild_data_initializes_partilhado(self, viewmodel):
        """Testa que coluna Partilhado é inicializada."""
        viewmodel.rebuild_data(1, 100, 100)

        row_data = viewmodel.get_row_data(0)
        assert row_data is not None
        assert "Partilhado" in row_data
        assert row_data["Partilhado"]["partilhado"] is False

    def test_rebuild_data_emits_signals(self, viewmodel, qtbot):
        """Testa que sinais são emitidos ao reconstruir."""
        with qtbot.waitSignal(viewmodel.table_rebuilt, timeout=1000):
            with qtbot.waitSignal(viewmodel.data_changed, timeout=1000):
                viewmodel.rebuild_data(2, 100, 101)

    def test_rebuild_data_clears_previous_data(self, viewmodel):
        """Testa que dados anteriores são limpos."""
        # Cria dados iniciais
        viewmodel.rebuild_data(3, 100, 102)
        viewmodel.set_cell_value(0, "Setúbal", "100")

        # Reconstrói com novos dados
        viewmodel.rebuild_data(2, 200, 201)

        assert viewmodel.row_count == 2
        # Novo primeiro recibo deve ser 200, não 100
        assert viewmodel.get_cell_value(0, "Recibo") == "200"
        # Valores devem estar resetados
        assert viewmodel.get_cell_value(0, "Setúbal") == "0"


class TestSetCellValue:
    """Testes de definição de valor de célula."""

    def test_set_cell_value_valid_number(self, viewmodel):
        """Testa definição de valor numérico válido."""
        viewmodel.rebuild_data(1, 100, 100)

        result = viewmodel.set_cell_value(0, "Setúbal", "100")

        assert result is True
        assert viewmodel.get_cell_value(0, "Setúbal") == "100"

    def test_set_cell_value_normalizes_decimal(self, viewmodel):
        """Testa normalização de separador decimal."""
        viewmodel.rebuild_data(1, 100, 100)

        viewmodel.set_cell_value(0, "Setúbal", "100.50")

        # Deve normalizar ponto para vírgula
        assert viewmodel.get_cell_value(0, "Setúbal") == "100,50"

    def test_set_cell_value_invalid_number(self, viewmodel):
        """Testa que valor inválido é rejeitado."""
        viewmodel.rebuild_data(1, 100, 100)

        viewmodel.set_cell_value(0, "Setúbal", "abc")

        # Deve reverter para valor padrão
        assert viewmodel.get_cell_value(0, "Setúbal") == "0"

    def test_set_cell_value_negative_number(self, viewmodel):
        """Testa que número negativo é rejeitado."""
        viewmodel.rebuild_data(1, 100, 100)

        viewmodel.set_cell_value(0, "Setúbal", "-50")

        # Deve reverter para valor padrão
        assert viewmodel.get_cell_value(0, "Setúbal") == "0"

    def test_set_cell_value_empty_string(self, viewmodel):
        """Testa que string vazia usa valor padrão."""
        viewmodel.rebuild_data(1, 100, 100)

        viewmodel.set_cell_value(0, "Setúbal", "")

        assert viewmodel.get_cell_value(0, "Setúbal") == "0"

    def test_set_cell_value_whitespace(self, viewmodel):
        """Testa que espaços são tratados como vazios."""
        viewmodel.rebuild_data(1, 100, 100)

        viewmodel.set_cell_value(0, "Setúbal", "   ")

        assert viewmodel.get_cell_value(0, "Setúbal") == "0"

    def test_set_cell_value_recalculates_totals(self, viewmodel):
        """Testa que totais são recalculados ao definir valor."""
        viewmodel.rebuild_data(2, 100, 101)

        viewmodel.set_cell_value(0, "Setúbal", "100")
        viewmodel.set_cell_value(1, "Setúbal", "50")

        totals = viewmodel.get_totals()
        assert totals["Setúbal"] == 150.0

    def test_set_cell_value_emits_signal(self, viewmodel, qtbot):
        """Testa que sinal é emitido ao definir valor."""
        viewmodel.rebuild_data(1, 100, 100)

        with qtbot.waitSignal(viewmodel.data_changed, timeout=1000):
            viewmodel.set_cell_value(0, "Setúbal", "100")

    def test_set_cell_value_invalid_row(self, viewmodel):
        """Testa que linha inválida é rejeitada."""
        viewmodel.rebuild_data(1, 100, 100)

        result = viewmodel.set_cell_value(10, "Setúbal", "100")

        assert result is False

    def test_set_cell_value_invalid_column(self, viewmodel):
        """Testa que coluna inválida é rejeitada."""
        viewmodel.rebuild_data(1, 100, 100)

        result = viewmodel.set_cell_value(0, "ColunaNaoExiste", "100")

        assert result is False

    def test_set_cell_value_recibo_column(self, viewmodel):
        """Testa que coluna Recibo não é editável."""
        viewmodel.rebuild_data(1, 100, 100)

        result = viewmodel.set_cell_value(0, "Recibo", "999")

        assert result is False
        # Valor não deve ter mudado
        assert viewmodel.get_cell_value(0, "Recibo") == "100"


class TestCalculateTotals:
    """Testes de cálculo de totais."""

    def test_calculate_totals_single_value(self, viewmodel):
        """Testa cálculo de totais com um valor."""
        viewmodel.rebuild_data(1, 100, 100)
        viewmodel.set_cell_value(0, "Setúbal", "100,50")

        totals = viewmodel.get_totals()

        assert totals["Setúbal"] == 100.5

    def test_calculate_totals_multiple_values(self, viewmodel):
        """Testa cálculo de totais com múltiplos valores."""
        viewmodel.rebuild_data(3, 100, 102)
        viewmodel.set_cell_value(0, "Setúbal", "50")
        viewmodel.set_cell_value(1, "Setúbal", "75,50")
        viewmodel.set_cell_value(2, "Setúbal", "24,50")

        totals = viewmodel.get_totals()

        assert totals["Setúbal"] == 150.0

    def test_calculate_totals_multiple_columns(self, viewmodel):
        """Testa cálculo de totais em múltiplas colunas."""
        viewmodel.rebuild_data(2, 100, 101)
        viewmodel.set_cell_value(0, "Setúbal", "100")
        viewmodel.set_cell_value(1, "Setúbal", "50")
        viewmodel.set_cell_value(0, "Santarém", "25")
        viewmodel.set_cell_value(1, "Santarém", "75")

        totals = viewmodel.get_totals()

        assert totals["Setúbal"] == 150.0
        assert totals["Santarém"] == 100.0

    def test_calculate_totals_ignores_invalid_values(self, viewmodel):
        """Testa que valores inválidos são ignorados no cálculo."""
        viewmodel.rebuild_data(2, 100, 101)
        viewmodel.set_cell_value(0, "Setúbal", "100")
        # Força valor inválido diretamente nos dados (bypass validação)
        viewmodel._data[1]["Setúbal"] = "abc"

        viewmodel._calculate_totals()
        totals = viewmodel.get_totals()

        # Deve somar apenas o valor válido
        assert totals["Setúbal"] == 100.0

    def test_calculate_totals_emits_signal(self, viewmodel, qtbot):
        """Testa que sinal é emitido ao calcular totais."""
        viewmodel.rebuild_data(1, 100, 100)

        with qtbot.waitSignal(viewmodel.totals_updated, timeout=1000):
            viewmodel.set_cell_value(0, "Setúbal", "100")

    def test_get_formatted_totals(self, viewmodel):
        """Testa formatação de totais como moeda."""
        viewmodel.rebuild_data(2, 100, 101)
        viewmodel.set_cell_value(0, "Setúbal", "100")
        viewmodel.set_cell_value(1, "Setúbal", "50,50")

        formatted = viewmodel.get_formatted_totals()

        assert "150,50" in formatted["Setúbal"]
        assert "€" in formatted["Setúbal"]


class TestGetData:
    """Testes de obtenção de dados."""

    def test_get_data_empty(self, viewmodel):
        """Testa obtenção de dados de tabela vazia."""
        data = viewmodel.get_data()

        assert data == []

    def test_get_data_single_row(self, viewmodel):
        """Testa obtenção de dados de uma linha."""
        viewmodel.rebuild_data(1, 100, 100)
        viewmodel.set_cell_value(0, "Setúbal", "100")

        data = viewmodel.get_data()

        assert len(data) == 1
        assert data[0]["Recibo"] == "100"
        assert data[0]["Setúbal"] == "100"

    def test_get_data_multiple_rows(self, viewmodel):
        """Testa obtenção de dados de múltiplas linhas."""
        viewmodel.rebuild_data(3, 100, 102)

        data = viewmodel.get_data()

        assert len(data) == 3
        assert data[0]["Recibo"] == "100"
        assert data[1]["Recibo"] == "101"
        assert data[2]["Recibo"] == "102"

    def test_get_row_data_valid(self, viewmodel):
        """Testa obtenção de dados de linha específica."""
        viewmodel.rebuild_data(2, 100, 101)
        viewmodel.set_cell_value(1, "Setúbal", "75")

        row_data = viewmodel.get_row_data(1)

        assert row_data is not None
        assert row_data["Recibo"] == "101"
        assert row_data["Setúbal"] == "75"

    def test_get_row_data_invalid_row(self, viewmodel):
        """Testa obtenção de dados de linha inválida."""
        viewmodel.rebuild_data(1, 100, 100)

        row_data = viewmodel.get_row_data(10)

        assert row_data is None

    def test_get_cell_value_valid(self, viewmodel):
        """Testa obtenção de valor de célula específica."""
        viewmodel.rebuild_data(1, 100, 100)
        viewmodel.set_cell_value(0, "Setúbal", "100")

        value = viewmodel.get_cell_value(0, "Setúbal")

        assert value == "100"

    def test_get_cell_value_invalid_row(self, viewmodel):
        """Testa obtenção de célula com linha inválida."""
        viewmodel.rebuild_data(1, 100, 100)

        value = viewmodel.get_cell_value(10, "Setúbal")

        assert value == ""

    def test_get_cell_value_invalid_column(self, viewmodel):
        """Testa obtenção de célula com coluna inválida."""
        viewmodel.rebuild_data(1, 100, 100)

        value = viewmodel.get_cell_value(0, "ColunaNaoExiste")

        assert value == ""


class TestSetPartilhadoData:
    """Testes de definição de dados partilhados."""

    def test_set_partilhado_data_valid(self, viewmodel):
        """Testa definição de dados de partilha."""
        viewmodel.rebuild_data(1, 100, 100)

        partilhado_data = {
            "partilhado": True,
            "tecnico_20": "João",
            "tecnico_30": "Maria",
        }
        viewmodel.set_partilhado_data(0, partilhado_data)

        row_data = viewmodel.get_row_data(0)
        assert row_data["Partilhado"]["partilhado"] is True
        assert row_data["Partilhado"]["tecnico_20"] == "João"

    def test_set_partilhado_data_recalculates_totals(self, viewmodel, qtbot):
        """Testa que totais são recalculados ao definir partilha."""
        viewmodel.rebuild_data(1, 100, 100)

        with qtbot.waitSignal(viewmodel.totals_updated, timeout=1000):
            viewmodel.set_partilhado_data(0, {"partilhado": True, "tecnico_20": "", "tecnico_30": ""})

    def test_set_partilhado_data_invalid_row(self, viewmodel):
        """Testa que linha inválida é ignorada."""
        viewmodel.rebuild_data(1, 100, 100)

        # Não deve lançar exceção
        viewmodel.set_partilhado_data(10, {"partilhado": True, "tecnico_20": "", "tecnico_30": ""})


class TestClearData:
    """Testes de limpeza de dados."""

    def test_clear_data_removes_all(self, viewmodel):
        """Testa que limpar remove todos os dados."""
        viewmodel.rebuild_data(5, 100, 104)
        viewmodel.set_cell_value(0, "Setúbal", "100")

        viewmodel.clear_data()

        assert viewmodel.is_empty is True
        assert viewmodel.row_count == 0
        assert viewmodel.get_totals() == {}

    def test_clear_data_emits_signal(self, viewmodel, qtbot):
        """Testa que sinal é emitido ao limpar."""
        viewmodel.rebuild_data(1, 100, 100)

        with qtbot.waitSignal(viewmodel.data_changed, timeout=1000):
            viewmodel.clear_data()


class TestViewModelLifecycle:
    """Testes de ciclo de vida do ViewModel."""

    def test_on_appear_logs(self, viewmodel):
        """Testa que on_appear não lança exceção."""
        viewmodel.on_appear()  # Deve apenas logar

    def test_dispose_clears_resources(self, viewmodel):
        """Testa que dispose limpa recursos."""
        viewmodel.rebuild_data(5, 100, 104)
        viewmodel.set_cell_value(0, "Setúbal", "100")

        viewmodel.dispose()

        assert viewmodel.is_empty is True
        assert viewmodel.row_count == 0
