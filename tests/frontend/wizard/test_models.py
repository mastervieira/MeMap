"""Tests for wizard data models.

Tests for FormData, TableRowData, and WizardState.
"""

from __future__ import annotations

from decimal import Decimal

import pytest

from src.common.constants.enums import TipoDiaAssiduidade
from src.frontend.wizard.models import (
    FormData,
    TableRowData,
    WizardAction,
    WizardState,
)


class TestFormData:
    """Tests for FormData dataclass."""

    def test_create_valid_form_data(self) -> None:
        """Test creating valid FormData instance."""
        form_data = FormData(
            quantidade_recibos=5,
            recibo_inicio=100,
            recibo_fim=104,
            zona_primaria="Setúbal",
            zona_secundaria="Santarém",
            total_km=Decimal("150.5"),
        )

        assert form_data.quantidade_recibos == 5
        assert form_data.recibo_inicio == 100
        assert form_data.recibo_fim == 104
        assert form_data.zona_primaria == "Setúbal"
        assert form_data.total_km == Decimal("150.5")

    def test_form_data_validation_negative_quantidade(
        self,
    ) -> None:
        """Test validation fails for negative quantidade."""
        with pytest.raises(ValueError, match="non-negative"):
            FormData(
                quantidade_recibos=-1,
                recibo_inicio=100,
                recibo_fim=104,
                zona_primaria="Setúbal",
                zona_secundaria="",
            )

    def test_form_data_validation_fim_before_inicio(
        self,
    ) -> None:
        """Test validation fails when fim < inicio."""
        with pytest.raises(ValueError, match=">="):
            FormData(
                quantidade_recibos=1,
                recibo_inicio=100,
                recibo_fim=99,
                zona_primaria="Setúbal",
                zona_secundaria="",
            )

    def test_form_data_to_dict(self) -> None:
        """Test converting FormData to dictionary."""
        form_data = FormData(
            quantidade_recibos=3,
            recibo_inicio=100,
            recibo_fim=102,
            zona_primaria="Évora",
            zona_secundaria="",
        )

        data_dict = form_data.to_dict()

        assert data_dict["quantidade_recibos"] == 3
        assert data_dict["recibo_inicio"] == 100
        assert data_dict["zona_primaria"] == "Évora"

    def test_form_data_from_dict(self) -> None:
        """Test creating FormData from dictionary."""
        data_dict = {
            "quantidade_recibos": 2,
            "recibo_inicio": 50,
            "recibo_fim": 51,
            "zona_primaria": "Santarém",
            "zona_secundaria": "Évora",
            "total_km": 75.0,
        }

        form_data = FormData.from_dict(data_dict)

        assert form_data.quantidade_recibos == 2
        assert form_data.recibo_inicio == 50
        assert form_data.total_km == Decimal("75.0")


class TestTableRowData:
    """Tests for TableRowData dataclass."""

    def test_create_valid_table_row(self) -> None:
        """Test creating valid TableRowData instance."""
        row = TableRowData(
            dia=15,
            dia_semana="Segunda",
            tipo=TipoDiaAssiduidade.TRABALHO,
            recibo_inicio=100,
            recibo_fim=105,
            ips=25,
            valor_com_iva=Decimal("500.00"),
        )

        assert row.dia == 15
        assert row.dia_semana == "Segunda"
        assert row.ips == 25
        assert row.is_work_day is True

    def test_table_row_num_recibos(self) -> None:
        """Test num_recibos property calculation."""
        row = TableRowData(
            dia=1,
            dia_semana="Terça",
            recibo_inicio=10,
            recibo_fim=14,
        )

        assert row.num_recibos == 5

    def test_table_row_validation_invalid_dia(self) -> None:
        """Test validation fails for invalid dia."""
        with pytest.raises(ValueError, match="between 1 and 31"):
            TableRowData(dia=0, dia_semana="Quarta")

        with pytest.raises(ValueError, match="between 1 and 31"):
            TableRowData(dia=32, dia_semana="Quinta")

    def test_table_row_to_dict(self) -> None:
        """Test converting TableRowData to dictionary."""
        row = TableRowData(
            dia=10, dia_semana="Sexta", ips=10
        )

        data_dict = row.to_dict()

        assert data_dict["dia"] == 10
        assert data_dict["dia_semana"] == "Sexta"
        assert data_dict["tipo"] == "trabalho"

    def test_table_row_from_dict(self) -> None:
        """Test creating TableRowData from dictionary."""
        data_dict = {
            "dia": 20,
            "dia_semana": "Sábado",
            "tipo": "sabado",
            "ips": 0,
        }

        row = TableRowData.from_dict(data_dict)

        assert row.dia == 20
        assert row.tipo == TipoDiaAssiduidade.SABADO


class TestWizardState:
    """Tests for WizardState enum."""

    def test_wizard_state_values(self) -> None:
        """Test WizardState enum values."""
        assert WizardState.STAGE_1_FORM.value == "stage_1_form"
        assert (
            WizardState.STAGE_2_TABLE.value == "stage_2_table"
        )
        assert WizardState.COMPLETED.value == "completed"

    def test_wizard_state_is_active(self) -> None:
        """Test is_active property."""
        assert WizardState.STAGE_1_FORM.is_active is True
        assert WizardState.STAGE_2_TABLE.is_active is True
        assert WizardState.COMPLETED.is_active is False
        assert WizardState.CANCELLED.is_active is False

    def test_wizard_state_stage_number(self) -> None:
        """Test stage_number property."""
        assert WizardState.STAGE_1_FORM.stage_number == 1
        assert WizardState.STAGE_2_TABLE.stage_number == 2
        assert WizardState.STAGE_3_CALENDAR.stage_number == 3
        assert WizardState.COMPLETED.stage_number is None

    def test_wizard_state_can_advance(self) -> None:
        """Test can_advance_to method."""
        # Can advance from stage 1 to stage 2
        assert WizardState.STAGE_1_FORM.can_advance_to(
            WizardState.STAGE_2_TABLE
        )

        # Cannot advance from stage 1 to stage 3
        assert not WizardState.STAGE_1_FORM.can_advance_to(
            WizardState.STAGE_3_CALENDAR
        )

        # Can cancel from any stage
        assert WizardState.STAGE_2_TABLE.can_advance_to(
            WizardState.CANCELLED
        )


class TestWizardAction:
    """Tests for WizardAction enum."""

    def test_wizard_action_values(self) -> None:
        """Test WizardAction enum has expected values."""
        assert WizardAction.GO_NEXT is not None
        assert WizardAction.GO_BACK is not None
        assert WizardAction.COMPLETE is not None
        assert WizardAction.CANCEL is not None
