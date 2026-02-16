"""ValidationService - Data validation.

Handles all business data validation.
"""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import TYPE_CHECKING

from src.repositories.tabela_taxas_repository import TabelaTaxasRepository
from src.common.validators.recibo_validator import ReciboValidator

if TYPE_CHECKING:
    from src.db.models.mapas import TabelaTaxas
    from src.frontend.wizard.models import FormData, TableRowData
    from src.repositories.tabela_taxas_repository import (
        TabelaTaxasRepository,
    )

logger: logging.Logger = logging.getLogger(__name__)


class ValidationService:
    """Validates business data.

    Responsibilities:
    - Validate form data
    - Validate table rows
    - Validate receipt numbers
    - Validate dates
    - Check data consistency
    """

    def __init__(
        self, repository: TabelaTaxasRepository
    ) -> None:
        """Initialize ValidationService.

        Args:
            repository: TabelaTaxasRepository instance
        """
        self._repository: TabelaTaxasRepository = repository
        self._recibo_validator = ReciboValidator(repository)

    def validar_formulario(
        self, form_data: FormData
    ) -> tuple[bool, list[str]]:
        """Validate form data.

        Validates business rules beyond basic type checking.
        FormData.__post_init__ already validates basic types and
        consistency.

        Args:
            form_data: FormData instance to validate

        Returns:
            Tuple of (is_valid, list_of_error_messages)

        Example:
            >>> svc = ValidationService(repo)
            >>> form = FormData(quantidade_recibos=5, ...)
            >>> is_valid, errors = svc.validar_formulario(form)
            >>> if not is_valid:
            ...     print(errors)
        """
        errors: list[str] = []

        # FormData.__post_init__ já validou:
        # - quantidade_recibos >= 0
        # - recibo_inicio >= 0
        # - recibo_fim >= 0
        # - recibo_fim >= recibo_inicio
        # - total_km >= 0
        # - quantidade consistente com range

        # Validações adicionais de negócio
        if not form_data.zona_primaria.strip():
            errors.append(
                "Zona primária é obrigatória"
            )

        if not form_data.zona_secundaria.strip():
            errors.append(
                "Zona secundária é obrigatória"
            )

        # Validar range razoável de recibos (evitar ranges enormes)
        if form_data.quantidade_recibos > 1000:
            errors.append(
                f"Quantidade de recibos ({form_data.quantidade_recibos}) "
                "é muito alta. Máximo permitido: 1000"
            )

        return (len(errors) == 0, errors)

    def validar_linha_tabela(
        self, linha: TableRowData
    ) -> tuple[bool, str | None]:
        """Validate single table row.

        Validates that row has valid data (non-empty and consistent).

        Args:
            linha: TableRowData instance to validate

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> row = TableRowData(dia=15, dia_semana="Segunda", ...)
            >>> is_valid, error = svc.validar_linha_tabela(row)
        """
        # TableRowData.__post_init__ já validou:
        # - dia entre 1-31
        # - ips >= 0
        # - valor_com_iva >= 0
        # - km >= 0
        # - recibo_fim >= recibo_inicio

        # Verificar se linha tem dados válidos (não está vazia)
        if not self._is_row_non_empty(linha):
            return (
                False,
                f"Linha do dia {linha.dia} está vazia "
                "(todos os valores são 0)",
            )

        # Verificar consistência de recibos para dias de trabalho
        if linha.is_work_day:
            if linha.recibo_inicio is None or linha.recibo_fim is None:
                return (
                    False,
                    f"Dia de trabalho {linha.dia} deve ter "
                    "recibos início e fim definidos",
                )

            if linha.ips <= 0:
                return (
                    False,
                    f"Dia de trabalho {linha.dia} deve ter "
                    "pelo menos 1 IP processado",
                )

        return (True, None)

    def _is_row_non_empty(self, linha: TableRowData) -> bool:
        """Check if row has valid data (not empty).

        A row is considered empty if all numeric values are 0.

        Args:
            linha: TableRowData instance

        Returns:
            True if row has valid data
        """
        # Verificar se algum valor numérico é diferente de 0
        if linha.ips > 0:
            return True
        if linha.valor_com_iva > Decimal("0"):
            return True
        if linha.km > Decimal("0"):
            return True

        return False

    def validar_recibo(
        self,
        recibo_num: int,
        mes: int,
        ano: int,
        exclude_dia: int | None = None,
        current_table_data: list[dict[str, object]] | None = None,
    ) -> tuple[bool, str | None]:
        """Validate receipt number.

        Checks for duplicates in table, month, and history.
        Optionally excludes a specific day (for editing saved days).

        Args:
            recibo_num: Receipt number to validate
            mes: Month (1-12)
            ano: Year (e.g. 2026)
            exclude_dia: Day to exclude from duplicate check
                (used when editing)
            current_table_data: Current table data for in-table
                duplicate check

        Returns:
            Tuple of (is_valid, error_message)

        Example:
            >>> # Validate new receipt
            >>> is_valid, error = svc.validar_recibo(
            ...     1050, mes=2, ano=2026
            ... )
            >>> # Validate when editing day 15
            >>> is_valid, error = svc.validar_recibo(
            ...     1050, mes=2, ano=2026, exclude_dia=15
            ... )
        """
        result = self._recibo_validator.validate_recibo(
            recibo_num=recibo_num,
            current_table_data=current_table_data,
            mes=mes,
            ano=ano,
            dia_atual=exclude_dia,
        )

        if not result.is_valid:
            error_msg = " | ".join(result.errors)
            return (False, error_msg)

        return (True, None)

    def validar_range_recibos(
        self,
        recibo_inicio: int,
        recibo_fim: int,
        mes: int,
        ano: int,
    ) -> tuple[bool, list[str]]:
        """Validate range of receipt numbers.

        Validates entire range at once (for form validation).
        Checks if ANY receipt in the range already exists in BD.

        Args:
            recibo_inicio: Starting receipt number
            recibo_fim: Ending receipt number
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Returns:
            Tuple of (is_valid, list_of_error_messages)

        Example:
            >>> # Validate range 1001-1005
            >>> is_valid, errors = svc.validar_range_recibos(
            ...     1001, 1005, mes=2, ano=2026
            ... )
            >>> if not is_valid:
            ...     for error in errors:
            ...         print(f"⚠️ {error}")
        """
        errors: list[str] = []

        # Validar range básico
        if recibo_fim < recibo_inicio:
            errors.append(
                f"Recibo fim ({recibo_fim}) não pode ser "
                f"menor que recibo início ({recibo_inicio})"
            )
            return (False, errors)

        # Validar cada recibo no range
        recibos_duplicados: list[tuple[int, str]] = []

        for recibo_num in range(recibo_inicio, recibo_fim + 1):
            is_valid, error_msg = self.validar_recibo(
                recibo_num=recibo_num,
                mes=mes,
                ano=ano,
                exclude_dia=None,
                current_table_data=None,
            )

            if not is_valid:
                # Guardar recibo e mensagem de erro
                recibos_duplicados.append(
                    (recibo_num, error_msg or "Duplicado")
                )

        # Se houver duplicados, criar mensagem consolidada
        if recibos_duplicados:
            if len(recibos_duplicados) == 1:
                recibo, msg = recibos_duplicados[0]
                errors.append(
                    f"Recibo {recibo} já existe: {msg}"
                )
            else:
                # Múltiplos duplicados - listar os primeiros 5
                recibos_str = ", ".join(
                    str(r) for r, _ in recibos_duplicados[:5]
                )
                if len(recibos_duplicados) > 5:
                    recibos_str += (
                        f" e mais {len(recibos_duplicados) - 5}"
                    )

                errors.append(
                    f"❌ ATENÇÃO: {len(recibos_duplicados)} "
                    f"recibos já existem na BD!\n"
                    f"Recibos duplicados: {recibos_str}\n\n"
                    f"Verifique os números de recibo antes de "
                    f"continuar."
                )

        return (len(errors) == 0, errors)

    def validar_datas(self, mes: int, ano: int) -> bool:
        """Validate month and year.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Returns:
            True if valid, False otherwise

        Example:
            >>> svc.validar_datas(2, 2026)  # February 2026
            True
            >>> svc.validar_datas(13, 2026)  # Invalid month
            False
        """
        # Validar mês
        if not 1 <= mes <= 12:
            logger.warning(
                f"Mês inválido: {mes}. Deve estar entre 1 e 12"
            )
            return False

        # Validar ano (range razoável)
        if not 1900 <= ano <= 2100:
            logger.warning(
                f"Ano inválido: {ano}. Deve estar entre "
                "1900 e 2100"
            )
            return False

        return True

    def validar_consistencia_dados(
        self, tabela: TabelaTaxas
    ) -> tuple[bool, list[str]]:
        """Validate data consistency.

        Validates that wizard_data is well-formed and consistent
        with table lines.

        Args:
            tabela: TabelaTaxas instance to validate

        Returns:
            Tuple of (is_valid, list_of_error_messages)

        Example:
            >>> is_valid, errors = svc.validar_consistencia_dados(
            ...     mapa
            ... )
            >>> if not is_valid:
            ...     for error in errors:
            ...         print(f"  • {error}")
        """
        errors: list[str] = []

        # Validar estrutura de wizard_data
        if not isinstance(tabela.wizard_data, dict):
            errors.append(
                "wizard_data deve ser um dicionário"
            )
            return (False, errors)

        if "dias" not in tabela.wizard_data:
            errors.append(
                "wizard_data deve ter chave 'dias'"
            )
            return (False, errors)

        dias_data = tabela.wizard_data.get("dias", {})
        if not isinstance(dias_data, dict):
            errors.append(
                "wizard_data['dias'] deve ser um dicionário"
            )
            return (False, errors)

        # Validar que cada dia em wizard_data tem linha
        # correspondente
        for dia_str in dias_data.keys():
            try:
                dia = int(dia_str)
            except ValueError:
                errors.append(
                    f"Chave inválida em wizard_data['dias']: "
                    f"'{dia_str}' (deve ser número)"
                )
                continue

            # Verificar se dia está no range do mês
            if not 1 <= dia <= 31:
                errors.append(
                    f"Dia {dia} fora do range válido (1-31)"
                )

            # Verificar se existe linha correspondente
            linha_exists = any(
                linha.dia == dia for linha in tabela.linhas
            )
            if not linha_exists:
                errors.append(
                    f"Dia {dia} existe em wizard_data mas não "
                    "tem linha correspondente"
                )

        # Validar que cada linha tem dados em wizard_data
        for linha in tabela.linhas:
            dia_str = str(linha.dia)
            if dia_str not in dias_data:
                logger.warning(
                    f"Linha do dia {linha.dia} não tem dados "
                    "em wizard_data (pode ser dado legado)"
                )
                # Não adicionar como erro - dados legados
                # podem não ter wizard_data

        return (len(errors) == 0, errors)
