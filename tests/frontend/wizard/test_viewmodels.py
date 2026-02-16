"""Tests for wizard ViewModels.

Tests for FormViewModel, TableViewModel, CalendarViewModel,
and WizardCoordinator.
"""

from __future__ import annotations

from unittest.mock import Mock

import pytest
from PySide6.QtCore import QDate

from src.frontend.wizard.models import WizardState
from src.frontend.wizard.viewmodels import (
    CalendarViewModel,
    FormViewModel,
    TableViewModel,
    WizardCoordinator,
)


class TestFormViewModel:
    """Tests for FormViewModel."""

    @pytest.fixture
    def mock_data_service(self) -> Mock:
        """Create mock DataService."""
        return Mock()

    @pytest.fixture
    def mock_validation_service(self) -> Mock:
        """Create mock ValidationService."""
        return Mock()

    @pytest.fixture
    def form_viewmodel(
        self,
        mock_data_service: Mock,
        mock_validation_service: Mock,
    ) -> FormViewModel:
        """Create FormViewModel instance."""
        return FormViewModel(
            data_service=mock_data_service,
            validation_service=mock_validation_service,
        )

    def test_form_viewmodel_initialization(
        self,
        form_viewmodel: FormViewModel,
        mock_data_service: Mock,
    ) -> None:
        """Test FormViewModel initializes correctly."""
        assert form_viewmodel._data_service is mock_data_service
        assert form_viewmodel.form_data is None
        assert form_viewmodel.is_loading is False

    def test_form_viewmodel_properties(
        self, form_viewmodel: FormViewModel
    ) -> None:
        """Test FormViewModel properties."""
        assert form_viewmodel.form_data is None
        assert form_viewmodel.is_loading is False


class TestTableViewModel:
    """Tests for TableViewModel."""

    @pytest.fixture
    def mock_calculation_service(self) -> Mock:
        """Create mock CalculationService."""
        return Mock()

    @pytest.fixture
    def table_viewmodel(
        self, mock_calculation_service: Mock
    ) -> TableViewModel:
        """Create TableViewModel instance."""
        return TableViewModel(
            calculation_service=mock_calculation_service
        )

    def test_table_viewmodel_initialization(
        self,
        table_viewmodel: TableViewModel,
        mock_calculation_service: Mock,
    ) -> None:
        """Test TableViewModel initializes correctly."""
        assert (
            table_viewmodel._calculation_service
            is mock_calculation_service
        )
        assert table_viewmodel.table_rows == []
        assert table_viewmodel.is_loading is False


class TestCalendarViewModel:
    """Tests for CalendarViewModel."""

    @pytest.fixture
    def mock_validation_service(self) -> Mock:
        """Create mock ValidationService."""
        return Mock()

    @pytest.fixture
    def mock_export_service(self) -> Mock:
        """Create mock ExportService."""
        return Mock()

    @pytest.fixture
    def calendar_viewmodel(
        self,
        mock_validation_service: Mock,
        mock_export_service: Mock,
    ) -> CalendarViewModel:
        """Create CalendarViewModel instance."""
        return CalendarViewModel(
            validation_service=mock_validation_service,
            export_service=mock_export_service,
        )

    def test_calendar_viewmodel_initialization(
        self,
        calendar_viewmodel: CalendarViewModel,
        mock_export_service: Mock,
    ) -> None:
        """Test CalendarViewModel initializes correctly."""
        assert (
            calendar_viewmodel._export_service
            is mock_export_service
        )
        assert calendar_viewmodel.selected_date is None
        assert calendar_viewmodel.is_loading is False


class TestWizardCoordinator:
    """Tests for WizardCoordinator."""

    @pytest.fixture
    def mock_form_vm(self) -> Mock:
        """Create mock FormViewModel."""
        return Mock()

    @pytest.fixture
    def mock_table_vm(self) -> Mock:
        """Create mock TableViewModel."""
        return Mock()

    @pytest.fixture
    def mock_calendar_vm(self) -> Mock:
        """Create mock CalendarViewModel."""
        return Mock()

    @pytest.fixture
    def coordinator(
        self,
        mock_form_vm: Mock,
        mock_table_vm: Mock,
        mock_calendar_vm: Mock,
    ) -> WizardCoordinator:
        """Create WizardCoordinator instance."""
        return WizardCoordinator(
            form_viewmodel=mock_form_vm,
            table_viewmodel=mock_table_vm,
            calendar_viewmodel=mock_calendar_vm,
        )

    def test_coordinator_initialization(
        self,
        coordinator: WizardCoordinator,
        mock_form_vm: Mock,
    ) -> None:
        """Test WizardCoordinator initializes correctly."""
        assert coordinator._form_vm is mock_form_vm
        assert (
            coordinator.current_state == WizardState.STAGE_1_FORM
        )
        assert coordinator.current_stage == 1

    def test_coordinator_state_properties(
        self, coordinator: WizardCoordinator
    ) -> None:
        """Test WizardCoordinator state properties."""
        assert (
            coordinator.current_state == WizardState.STAGE_1_FORM
        )
        assert coordinator.current_stage == 1
