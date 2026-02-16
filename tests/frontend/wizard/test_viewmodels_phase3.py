"""Tests for Phase 3 ViewModels.

Comprehensive test suite for FormViewModel, TableViewModel, CalendarViewModel,
and WizardCoordinator implementations.
"""

from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, Mock, patch

import pytest
from PySide6.QtCore import QDate, QObject

from src.frontend.wizard.models import FormData, TableRowData, WizardState
from src.frontend.wizard.viewmodels import (
    CalendarViewModel,
    FormViewModel,
    TableViewModel,
    WizardCoordinator,
)


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def mock_validation_service() -> Mock:
    """Create mock ValidationService."""
    service = Mock()
    service.validar_formulario = Mock(return_value=(True, []))
    service.validar_datas = Mock(return_value=True)
    return service


@pytest.fixture
def mock_data_service() -> Mock:
    """Create mock DataService."""
    service = Mock()
    service.carregar_mapa = Mock(return_value=None)
    service.guardar_mapa = Mock()
    return service


@pytest.fixture
def mock_calculation_service() -> Mock:
    """Create mock CalculationService."""
    service = Mock()
    service.calcular_totais_tabela = Mock(
        return_value={
            "total_ips": Decimal("100"),
            "total_km": Decimal("250.5"),
            "total_valor": Decimal("1500.00"),
            "recibo_min": 1001,
            "recibo_max": 1005,
        }
    )
    return service


@pytest.fixture
def mock_export_service() -> Mock:
    """Create mock ExportService."""
    service = Mock()
    service.exportar_pdf = Mock(return_value="/path/to/file.pdf")
    service.exportar_excel = Mock(return_value="/path/to/file.xlsx")
    return service


@pytest.fixture
def sample_form_data() -> FormData:
    """Create sample FormData."""
    return FormData(
        quantidade_recibos=5,
        recibo_inicio=1001,
        recibo_fim=1005,
        zona_primaria="Setúbal",
        zona_secundaria="Lisboa",
        total_km=Decimal("250.50"),
    )


@pytest.fixture
def sample_table_row() -> TableRowData:
    """Create sample TableRowData."""
    return TableRowData(
        dia=15,
        dia_semana="Terça",
        tipo="trabalho",
        recibo_inicio=1001,
        recibo_fim=1005,
        ips=100,
        valor_com_iva=Decimal("1500.00"),
        locais="Setúbal",
        km=Decimal("50.00"),
        motivo="",
        periodo="09:00-17:00",
        observacoes="",
    )


# ============================================================================
# FORMVIEWMODEL TESTS
# ============================================================================


class TestFormViewModel:
    """Tests for FormViewModel."""

    def test_initialization(
        self, mock_data_service: Mock, mock_validation_service: Mock
    ) -> None:
        """Test FormViewModel initializes correctly."""
        vm = FormViewModel(mock_data_service, mock_validation_service)

        assert vm.form_data is None
        assert vm.is_loading is False
        assert vm._current_mes == 0
        assert vm._current_ano == 0

    def test_set_current_date(
        self, mock_data_service: Mock, mock_validation_service: Mock
    ) -> None:
        """Test setting current month/year."""
        vm = FormViewModel(mock_data_service, mock_validation_service)
        vm.set_current_date(2, 2026)

        assert vm._current_mes == 2
        assert vm._current_ano == 2026

    def test_on_validate_with_valid_data(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        sample_form_data: FormData,
    ) -> None:
        """Test validation with valid form data."""
        mock_validation_service.validar_formulario.return_value = (True, [])
        vm = FormViewModel(mock_data_service, mock_validation_service)
        vm._form_data = sample_form_data

        # Track signal emission
        success_emitted = False

        def on_success() -> None:
            nonlocal success_emitted
            success_emitted = True

        vm.validation_success.connect(on_success)
        vm.on_validate()

        assert success_emitted
        mock_validation_service.validar_formulario.assert_called_once_with(
            sample_form_data
        )

    def test_on_validate_with_invalid_data(
        self, mock_data_service: Mock, mock_validation_service: Mock
    ) -> None:
        """Test validation with invalid form data."""
        errors = ["Quantidade inválida", "Recibo duplicado"]
        mock_validation_service.validar_formulario.return_value = (False, errors)
        vm = FormViewModel(mock_data_service, mock_validation_service)
        vm._form_data = Mock()

        # Track signal emission
        error_emitted = False
        error_msg = ""

        def on_error(field: str, message: str) -> None:
            nonlocal error_emitted, error_msg
            error_emitted = True
            error_msg = message

        vm.validation_error.connect(on_error)
        vm.on_validate()

        assert error_emitted
        assert "Quantidade inválida" in error_msg
        assert "Recibo duplicado" in error_msg

    def test_on_validate_empty_form(
        self, mock_data_service: Mock, mock_validation_service: Mock
    ) -> None:
        """Test validation with empty form."""
        vm = FormViewModel(mock_data_service, mock_validation_service)

        error_emitted = False

        def on_error(field: str, message: str) -> None:
            nonlocal error_emitted
            error_emitted = True
            assert message == "Formulário vazio"

        vm.validation_error.connect(on_error)
        vm.on_validate()

        assert error_emitted

    def test_on_clear(
        self, mock_data_service: Mock, mock_validation_service: Mock
    ) -> None:
        """Test clearing form data."""
        vm = FormViewModel(mock_data_service, mock_validation_service)
        vm._form_data = Mock()
        vm._raw_form_data = {"some": "data"}

        cleared_emitted = False

        def on_cleared(field: str) -> None:
            nonlocal cleared_emitted
            cleared_emitted = True

        vm.validation_cleared.connect(on_cleared)
        vm.on_clear()

        assert vm.form_data is None
        assert vm._raw_form_data == {}
        assert cleared_emitted

    @patch("src.frontend.wizard.viewmodels.form_viewmodel.logger")
    def test_on_load_data_no_date_set(
        self,
        mock_logger: Mock,
        mock_data_service: Mock,
        mock_validation_service: Mock,
    ) -> None:
        """Test loading data without date set."""
        vm = FormViewModel(mock_data_service, mock_validation_service)

        error_emitted = False

        def on_error(field: str, message: str) -> None:
            nonlocal error_emitted
            error_emitted = True

        vm.validation_error.connect(on_error)
        vm.on_load_data()

        assert error_emitted


# ============================================================================
# TABLEVIEWMODEL TESTS
# ============================================================================


class TestTableViewModel:
    """Tests for TableViewModel."""

    def test_initialization(self, mock_calculation_service: Mock) -> None:
        """Test TableViewModel initializes correctly."""
        vm = TableViewModel(mock_calculation_service)

        assert vm.table_rows == []
        assert vm.is_loading is False

    def test_on_add_row(
        self, mock_calculation_service: Mock, sample_table_row: TableRowData
    ) -> None:
        """Test adding row to table."""
        vm = TableViewModel(mock_calculation_service)

        row_added_emitted = False
        added_index = -1

        def on_row_added(index: int) -> None:
            nonlocal row_added_emitted, added_index
            row_added_emitted = True
            added_index = index

        vm.row_added.connect(on_row_added)
        vm.on_add_row(sample_table_row)

        assert row_added_emitted
        assert added_index == 0
        assert len(vm.table_rows) == 1
        assert vm.table_rows[0].dia == 15

    def test_on_add_multiple_rows(
        self, mock_calculation_service: Mock, sample_table_row: TableRowData
    ) -> None:
        """Test adding multiple rows."""
        vm = TableViewModel(mock_calculation_service)

        row1 = sample_table_row
        row2 = TableRowData(
            dia=16,
            dia_semana="Quarta",
            tipo="trabalho",
            recibo_inicio=1006,
            recibo_fim=1010,
            ips=100,
            valor_com_iva=Decimal("1500.00"),
            locais="Setúbal",
            km=Decimal("50.00"),
            motivo="",
            periodo="09:00-17:00",
            observacoes="",
        )

        vm.on_add_row(row1)
        vm.on_add_row(row2)

        assert len(vm.table_rows) == 2
        assert vm.table_rows[0].dia == 15
        assert vm.table_rows[1].dia == 16

    def test_on_remove_row(
        self, mock_calculation_service: Mock, sample_table_row: TableRowData
    ) -> None:
        """Test removing row from table."""
        vm = TableViewModel(mock_calculation_service)
        vm.on_add_row(sample_table_row)

        row_removed_emitted = False
        removed_index = -1

        def on_row_removed(index: int) -> None:
            nonlocal row_removed_emitted, removed_index
            row_removed_emitted = True
            removed_index = index

        vm.row_removed.connect(on_row_removed)
        vm.on_remove_row(0)

        assert row_removed_emitted
        assert removed_index == 0
        assert len(vm.table_rows) == 0

    def test_on_remove_row_invalid_index(
        self, mock_calculation_service: Mock
    ) -> None:
        """Test removing row with invalid index."""
        vm = TableViewModel(mock_calculation_service)

        row_removed_emitted = False

        def on_row_removed(index: int) -> None:
            nonlocal row_removed_emitted
            row_removed_emitted = True

        vm.row_removed.connect(on_row_removed)
        vm.on_remove_row(0)  # Empty table

        assert not row_removed_emitted
        assert len(vm.table_rows) == 0

    def test_on_update_row(
        self, mock_calculation_service: Mock, sample_table_row: TableRowData
    ) -> None:
        """Test updating row in table."""
        vm = TableViewModel(mock_calculation_service)
        vm.on_add_row(sample_table_row)

        updated_row = TableRowData(
            dia=15,
            dia_semana="Terça",
            tipo="férias",
            recibo_inicio=0,
            recibo_fim=0,
            ips=0,
            valor_com_iva=Decimal("0"),
            locais="",
            km=Decimal("0"),
            motivo="Férias",
            periodo="",
            observacoes="",
        )

        changed_emitted = False

        def on_changed(rows: list) -> None:
            nonlocal changed_emitted
            changed_emitted = True

        vm.table_data_changed.connect(on_changed)
        vm.on_update_row(0, updated_row)

        assert changed_emitted
        assert vm.table_rows[0].tipo == "férias"
        assert vm.table_rows[0].motivo == "Férias"

    def test_on_calculate_totals_empty_table(
        self, mock_calculation_service: Mock
    ) -> None:
        """Test calculating totals with empty table."""
        vm = TableViewModel(mock_calculation_service)

        totals_emitted = False
        totals_data = {}

        def on_totals_updated(totals: dict) -> None:
            nonlocal totals_emitted, totals_data
            totals_emitted = True
            totals_data = totals

        vm.totals_updated.connect(on_totals_updated)
        vm.on_calculate_totals()

        assert totals_emitted
        assert totals_data["total_ips"] == Decimal("0")
        assert totals_data["total_km"] == Decimal("0")
        assert totals_data["total_valor"] == Decimal("0")
        assert totals_data["recibo_min"] is None
        assert totals_data["recibo_max"] is None

    def test_on_calculate_totals_with_rows(
        self,
        mock_calculation_service: Mock,
        sample_table_row: TableRowData,
    ) -> None:
        """Test calculating totals with rows."""
        vm = TableViewModel(mock_calculation_service)
        vm.on_add_row(sample_table_row)

        mock_calculation_service.calcular_totais_tabela.reset_mock()

        totals_emitted = False

        def on_totals_updated(totals: dict) -> None:
            nonlocal totals_emitted
            totals_emitted = True

        vm.totals_updated.connect(on_totals_updated)
        vm.on_calculate_totals()

        assert totals_emitted
        mock_calculation_service.calcular_totais_tabela.assert_called_once()

    def test_on_clear_all(
        self, mock_calculation_service: Mock, sample_table_row: TableRowData
    ) -> None:
        """Test clearing all rows."""
        vm = TableViewModel(mock_calculation_service)
        vm.on_add_row(sample_table_row)

        assert len(vm.table_rows) == 1

        cleared_emitted = False

        def on_cleared(rows: list) -> None:
            nonlocal cleared_emitted
            cleared_emitted = True

        vm.table_data_changed.connect(on_cleared)
        vm.on_clear_all()

        assert cleared_emitted
        assert len(vm.table_rows) == 0


# ============================================================================
# CALENDARVIEWMODEL TESTS
# ============================================================================


class TestCalendarViewModel:
    """Tests for CalendarViewModel."""

    def test_initialization(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test CalendarViewModel initializes correctly."""
        vm = CalendarViewModel(mock_validation_service, mock_export_service)

        assert vm.selected_date is None
        assert vm.is_loading is False

    def test_on_date_selected(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test selecting date."""
        vm = CalendarViewModel(mock_validation_service, mock_export_service)
        test_date = QDate(2026, 2, 15)

        date_selected_emitted = False
        selected_date = None

        def on_date_selected(date: QDate) -> None:
            nonlocal date_selected_emitted, selected_date
            date_selected_emitted = True
            selected_date = date

        vm.date_selected.connect(on_date_selected)
        vm.on_date_selected(test_date)

        assert date_selected_emitted
        assert selected_date == test_date
        assert vm.selected_date == test_date

    def test_on_date_selected_invalid(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test selecting invalid date."""
        vm = CalendarViewModel(mock_validation_service, mock_export_service)
        invalid_date = QDate()  # Invalid date

        date_selected_emitted = False

        def on_date_selected(date: QDate) -> None:
            nonlocal date_selected_emitted
            date_selected_emitted = True

        vm.date_selected.connect(on_date_selected)
        vm.on_date_selected(invalid_date)

        assert not date_selected_emitted

    def test_on_mark_day(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test marking day."""
        mock_validation_service.validar_datas.return_value = True
        vm = CalendarViewModel(mock_validation_service, mock_export_service)
        test_date = QDate(2026, 2, 15)

        day_marked_emitted = False
        marked_date = None
        marked_tipo = ""

        def on_day_marked(date: QDate, tipo: str) -> None:
            nonlocal day_marked_emitted, marked_date, marked_tipo
            day_marked_emitted = True
            marked_date = date
            marked_tipo = tipo

        vm.day_marked.connect(on_day_marked)
        vm.on_mark_day(test_date, "trabalho")

        assert day_marked_emitted
        assert marked_date == test_date
        assert marked_tipo == "trabalho"

    def test_on_mark_day_invalid_date(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test marking invalid date."""
        vm = CalendarViewModel(mock_validation_service, mock_export_service)
        invalid_date = QDate()

        error_emitted = False

        def on_error(message: str) -> None:
            nonlocal error_emitted
            error_emitted = True

        vm.error_occurred.connect(on_error)
        vm.on_mark_day(invalid_date, "trabalho")

        assert error_emitted

    def test_on_export_pdf_blocked(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test PDF export is blocked."""
        vm = CalendarViewModel(mock_validation_service, mock_export_service)

        export_error_emitted = False
        error_msg = ""

        def on_export_error(message: str) -> None:
            nonlocal export_error_emitted, error_msg
            export_error_emitted = True
            error_msg = message

        vm.export_error.connect(on_export_error)
        vm.on_export_pdf("template.pdf")

        assert export_error_emitted
        assert "Phase 2" in error_msg

    def test_on_export_excel_blocked(
        self, mock_validation_service: Mock, mock_export_service: Mock
    ) -> None:
        """Test Excel export is blocked."""
        vm = CalendarViewModel(mock_validation_service, mock_export_service)

        export_error_emitted = False

        def on_export_error(message: str) -> None:
            nonlocal export_error_emitted
            export_error_emitted = True

        vm.export_error.connect(on_export_error)
        vm.on_export_excel()

        assert export_error_emitted


# ============================================================================
# WIZARDCOORDINATOR TESTS
# ============================================================================


class TestWizardCoordinator:
    """Tests for WizardCoordinator."""

    def test_initialization(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test WizardCoordinator initializes correctly."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        assert coordinator.current_state == WizardState.STAGE_1_FORM
        assert coordinator.current_stage == 1

    def test_on_next_stage(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
        sample_table_row: TableRowData,
    ) -> None:
        """Test advancing to next stage."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        table_vm.on_add_row(sample_table_row)  # Add row to pass validation
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        stage_changed_emitted = False
        new_stage = 0

        def on_stage_changed(stage: int) -> None:
            nonlocal stage_changed_emitted, new_stage
            stage_changed_emitted = True
            new_stage = stage

        coordinator.stage_changed.connect(on_stage_changed)
        coordinator.on_next_stage()

        assert stage_changed_emitted
        assert new_stage == 2
        assert coordinator.current_stage == 2

    def test_on_next_stage_empty_table_fails(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test advancing to table stage with empty table fails."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)
        coordinator._current_state = WizardState.STAGE_2_TABLE

        error_emitted = False

        def on_error(message: str) -> None:
            nonlocal error_emitted
            error_emitted = True

        coordinator.error_occurred.connect(on_error)
        coordinator.on_next_stage()

        assert error_emitted
        assert coordinator.current_stage == 2  # Still on stage 2

    def test_on_previous_stage(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test going back to previous stage."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)
        coordinator._current_state = WizardState.STAGE_2_TABLE

        stage_changed_emitted = False

        def on_stage_changed(stage: int) -> None:
            nonlocal stage_changed_emitted
            stage_changed_emitted = True

        coordinator.stage_changed.connect(on_stage_changed)
        coordinator.on_previous_stage()

        assert stage_changed_emitted
        assert coordinator.current_stage == 1

    def test_on_go_to_stage(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test going to specific stage."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        stage_changed_emitted = False

        def on_stage_changed(stage: int) -> None:
            nonlocal stage_changed_emitted
            stage_changed_emitted = True

        coordinator.stage_changed.connect(on_stage_changed)
        # Can only go to stage 2 from stage 1 (can't skip stages)
        coordinator.on_go_to_stage(2)

        assert stage_changed_emitted
        assert coordinator.current_stage == 2

    def test_on_complete_wizard(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test completing wizard."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)
        coordinator._current_state = WizardState.STAGE_3_CALENDAR

        wizard_completed_emitted = False

        def on_completed() -> None:
            nonlocal wizard_completed_emitted
            wizard_completed_emitted = True

        coordinator.wizard_completed.connect(on_completed)
        coordinator.on_complete_wizard()

        assert wizard_completed_emitted
        assert coordinator.current_state == WizardState.COMPLETED

    def test_on_cancel_wizard(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test cancelling wizard."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        wizard_cancelled_emitted = False

        def on_cancelled() -> None:
            nonlocal wizard_cancelled_emitted
            wizard_cancelled_emitted = True

        coordinator.wizard_cancelled.connect(on_cancelled)
        coordinator.on_cancel_wizard()

        assert wizard_cancelled_emitted
        assert coordinator.current_state == WizardState.CANCELLED

    def test_on_save_draft(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test saving draft."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        error_emitted = False

        def on_error(message: str) -> None:
            nonlocal error_emitted
            error_emitted = True

        coordinator.error_occurred.connect(on_error)
        coordinator.on_save_draft()

        # Currently emits error as placeholder
        assert error_emitted

    def test_on_load_draft(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test loading draft."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        error_emitted = False

        def on_error(message: str) -> None:
            nonlocal error_emitted
            error_emitted = True

        coordinator.error_occurred.connect(on_error)
        coordinator.on_load_draft(2, 2026)

        # Currently emits error as placeholder
        assert error_emitted

    def test_validate_current_stage_form(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test validating stage 1 (always valid)."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)

        assert coordinator._validate_current_stage() is True

    def test_validate_current_stage_table_empty(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
    ) -> None:
        """Test validating stage 2 with empty table."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)
        coordinator._current_state = WizardState.STAGE_2_TABLE

        assert coordinator._validate_current_stage() is False

    def test_validate_current_stage_table_with_rows(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
        mock_calculation_service: Mock,
        mock_export_service: Mock,
        sample_table_row: TableRowData,
    ) -> None:
        """Test validating stage 2 with rows."""
        form_vm = FormViewModel(mock_data_service, mock_validation_service)
        table_vm = TableViewModel(mock_calculation_service)
        table_vm.on_add_row(sample_table_row)
        calendar_vm = CalendarViewModel(
            mock_validation_service, mock_export_service
        )

        coordinator = WizardCoordinator(form_vm, table_vm, calendar_vm)
        coordinator._current_state = WizardState.STAGE_2_TABLE

        assert coordinator._validate_current_stage() is True
