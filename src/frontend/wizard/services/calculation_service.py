"""CalculationService - Business calculations.

Handles all financial and statistical calculations.
"""

from __future__ import annotations

import calendar
import logging
from decimal import Decimal
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.db.models.mapas import TabelaTaxas
    from src.frontend.wizard.models import TableRowData

logger: logging.Logger = logging.getLogger(__name__)

# Feriados fixos em Portugal (simplificado)
# TODO: Usar biblioteca holidays para feriados dinâmicos (Páscoa, etc.)
FERIADOS_FIXOS_PT: set[tuple[int, int]] = {
    (1, 1),    # Ano Novo
    (4, 25),   # 25 de Abril
    (5, 1),    # Dia do Trabalhador
    (6, 10),   # Dia de Portugal
    (8, 15),   # Assunção de Maria
    (10, 5),   # Implantação da República
    (11, 1),   # Todos os Santos
    (12, 1),   # Restauração da Independência
    (12, 8),   # Imaculada Conceição
    (12, 25),  # Natal
}


class CalculationService:
    """Performs business calculations.

    Responsibilities:
    - Calculate table totals
    - Calculate monthly totals
    - Convert values with/without VAT
    - Calculate total kilometers
    - Count working days
    """

    def __init__(self) -> None:
        """Initialize CalculationService.

        No dependencies required - pure calculation service.
        """
        pass

    def calcular_totais_tabela(
        self, linhas: list[TableRowData]
    ) -> dict[str, Decimal | int | None]:
        """Calculate totals for table rows.

        Calculates aggregated values for all rows in the table.

        Args:
            linhas: List of table rows

        Returns:
            Dictionary with calculated totals:
            - total_ips: Total number of IPs (Decimal)
            - total_km: Total kilometers (Decimal)
            - total_valor: Total value with VAT (Decimal)
            - recibo_min: Minimum receipt number (int | None)
            - recibo_max: Maximum receipt number (int | None)

        Example:
            >>> rows = [
            ...     TableRowData(dia=1, ips=10, km=Decimal("50"), ...),
            ...     TableRowData(dia=2, ips=15, km=Decimal("75"), ...),
            ... ]
            >>> svc = CalculationService()
            >>> totals = svc.calcular_totais_tabela(rows)
            >>> print(totals["total_ips"])
            25
        """
        total_ips: int = 0
        total_km: Decimal = Decimal("0")
        total_valor: Decimal = Decimal("0")
        recibo_min: int | None = None
        recibo_max: int | None = None

        for linha in linhas:
            # Somar IPs
            total_ips += linha.ips

            # Somar KM
            total_km += linha.km

            # Somar valor
            total_valor += linha.valor_com_iva

            # Calcular min/max de recibos
            if linha.recibo_inicio is not None:
                if recibo_min is None or linha.recibo_inicio < recibo_min:
                    recibo_min = linha.recibo_inicio

            if linha.recibo_fim is not None:
                if recibo_max is None or linha.recibo_fim > recibo_max:
                    recibo_max = linha.recibo_fim

        return {
            "total_ips": Decimal(total_ips),
            "total_km": total_km,
            "total_valor": total_valor,
            "recibo_min": recibo_min,
            "recibo_max": recibo_max,
        }

    def calcular_total_mes(
        self, tabela: TabelaTaxas
    ) -> Decimal:
        """Calculate total for entire month.

        Uses the pre-calculated total_faturacao from TabelaTaxas.

        Args:
            tabela: TabelaTaxas instance

        Returns:
            Total monthly value (faturacao total)

        Example:
            >>> svc = CalculationService()
            >>> total = svc.calcular_total_mes(mapa)
        """
        # TabelaTaxas já tem total_faturacao calculado
        # pelo repository.recalcular_totais()
        return tabela.total_faturacao

    def converter_com_iva_para_sem_iva(
        self, valor: Decimal, taxa_iva: Decimal
    ) -> Decimal:
        """Convert value from with VAT to without VAT.

        Formula: valor_sem_iva = valor_com_iva / (1 + taxa_iva/100)

        Args:
            valor: Value with VAT
            taxa_iva: VAT rate (e.g. Decimal("23") for 23%)

        Returns:
            Value without VAT

        Example:
            >>> svc = CalculationService()
            >>> com_iva = Decimal("123")
            >>> taxa = Decimal("23")
            >>> sem_iva = svc.converter_com_iva_para_sem_iva(
            ...     com_iva, taxa
            ... )
            >>> print(sem_iva)  # Should be 100.00
            100.00
        """
        if taxa_iva < Decimal("0"):
            raise ValueError(
                f"Taxa de IVA deve ser >= 0, recebido: {taxa_iva}"
            )

        # Formula: valor_sem_iva = valor_com_iva / (1 + taxa/100)
        divisor = Decimal("1") + (taxa_iva / Decimal("100"))
        valor_sem_iva = valor / divisor

        # Arredondar para 2 casas decimais (cêntimos)
        return valor_sem_iva.quantize(Decimal("0.01"))

    def calcular_kilometros_totais(
        self, linhas: list[TableRowData]
    ) -> Decimal:
        """Calculate total kilometers.

        Sums km from all table rows.

        Args:
            linhas: List of table rows

        Returns:
            Total kilometers

        Example:
            >>> rows = [
            ...     TableRowData(..., km=Decimal("50")),
            ...     TableRowData(..., km=Decimal("75")),
            ... ]
            >>> svc = CalculationService()
            >>> total = svc.calcular_kilometros_totais(rows)
            >>> print(total)
            125
        """
        total_km: Decimal = Decimal("0")

        for linha in linhas:
            total_km += linha.km

        return total_km

    def calcular_dias_trabalhados(
        self, mes: int, ano: int
    ) -> int:
        """Calculate number of working days in month.

        Counts weekdays (Monday-Friday) excluding Portuguese
        public holidays.

        Note: Currently only handles fixed holidays. Dynamic
        holidays (Easter, Carnival, etc.) are not included.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Returns:
            Number of working days

        Example:
            >>> svc = CalculationService()
            >>> dias = svc.calcular_dias_trabalhados(2, 2026)
            >>> print(f"Fevereiro 2026 tem {dias} dias úteis")
        """
        if not 1 <= mes <= 12:
            raise ValueError(
                f"Mês inválido: {mes}. Deve estar entre 1 e 12"
            )

        if not 1900 <= ano <= 2100:
            raise ValueError(
                f"Ano inválido: {ano}. Deve estar entre "
                "1900 e 2100"
            )

        # Obter número de dias no mês
        num_dias = calendar.monthrange(ano, mes)[1]

        dias_trabalhados = 0

        for dia in range(1, num_dias + 1):
            # Obter dia da semana (0=Segunda, 6=Domingo)
            dia_semana = calendar.weekday(ano, mes, dia)

            # Verificar se é dia útil (Segunda-Sexta)
            is_weekday = dia_semana < 5  # 0-4 = Seg-Sex

            # Verificar se não é feriado
            is_not_holiday = (mes, dia) not in FERIADOS_FIXOS_PT

            if is_weekday and is_not_holiday:
                dias_trabalhados += 1

        logger.debug(
            f"{mes}/{ano}: {dias_trabalhados} dias úteis "
            f"(total: {num_dias} dias)"
        )

        return dias_trabalhados
