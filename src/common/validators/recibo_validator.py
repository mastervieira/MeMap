"""Validador para números de recibo.

Verifica:
- Formato numérico inteiro positivo
- Duplicação dentro da tabela atual
- Duplicação no mês atual (BD)
- Duplicação no histórico completo (BD) - recibo é ÚNICO globalmente

Uso:
    from src.common.validators.recibo_validator import ReciboValidator

    validator = ReciboValidator(repository)
    result = validator.validate_recibo(
        recibo_num=1050,
        current_table_data=[...],
        mes=2,
        ano=2026
    )

    if not result.is_valid:
        # Célula fica vermelha
        print(result.errors)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .base_validator import BaseValidator

if TYPE_CHECKING:
    from src.repositories.assiduidade_repository import MapaAssiduidadeRepository

logger = logging.getLogger(__name__)


@dataclass
class ReciboValidationResult:
    """Resultado da validação de número de recibo."""

    is_valid: bool = True
    recibo_num: int | None = None
    is_numeric: bool = True
    is_duplicate_in_table: bool = False
    is_duplicate_in_month: bool = False
    is_duplicate_in_history: bool = False
    duplicate_locations: list[str] = field(default_factory=list)  # ["Tabela", "Mês Atual", "Histórico"]
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def add_error(self, msg: str) -> None:
        """Adiciona erro e marca como inválido."""
        self.errors.append(msg)
        self.is_valid = False

    def add_warning(self, msg: str) -> None:
        """Adiciona aviso."""
        self.warnings.append(msg)


class ReciboValidator(BaseValidator):
    """Validador para números de recibo."""

    def __init__(self, repository: MapaAssiduidadeRepository | None = None) -> None:
        """Inicializa validador de recibos.

        Args:
            repository: Repository para verificar duplicados na BD
        """
        super().__init__()
        self._repository = repository
        self._validation_result: ReciboValidationResult | None = None

    def is_valid(self, data: dict[str, Any]) -> bool:
        """Valida recibo usando dicionário de entrada.

        Args:
            data: Dicionário com:
                - recibo_num: Número do recibo
                - current_table_data: Lista de dicts com dados da tabela atual
                - mes: Mês atual
                - ano: Ano atual
                - exclude_row: Índice da linha a excluir (ao validar edição)

        Returns:
            True se recibo é válido, False caso contrário
        """
        recibo_num = data.get("recibo_num")
        current_table_data = data.get("current_table_data", [])
        mes = data.get("mes")
        ano = data.get("ano")
        exclude_row = data.get("exclude_row")

        result = self.validate_recibo(
            recibo_num=recibo_num,
            current_table_data=current_table_data,
            mes=mes,
            ano=ano,
            exclude_row=exclude_row,
        )
        self._validation_result = result
        return result.is_valid

    def get_errors(self) -> dict[str, str]:
        """Obtém erros de validação.

        Returns:
            Dicionário com mensagens de erro
        """
        if self._validation_result is None:
            return {}

        errors = {}

        if self._validation_result.errors:
            errors["recibo"] = " | ".join(self._validation_result.errors)

        return errors

    def validate_recibo(
        self,
        recibo_num: int | str,
        current_table_data: list[dict[str, Any]] | None = None,
        mes: int | None = None,
        ano: int | None = None,
        exclude_row: int | None = None,
    ) -> ReciboValidationResult:
        """Valida número de recibo completo.

        Args:
            recibo_num: Número do recibo a validar
            current_table_data: Dados da tabela atual (para verificar duplicados locais)
            mes: Mês atual (para verificar duplicados no mês)
            ano: Ano atual (para verificar duplicados no mês)
            exclude_row: Índice da linha a excluir da verificação (ao editar)

        Returns:
            ReciboValidationResult com detalhes da validação
        """
        result = ReciboValidationResult()

        # 1. Validar formato numérico
        validated_num = self._validate_numeric(recibo_num, result)
        if validated_num is None:
            return result

        result.recibo_num = validated_num

        # 2. Verificar duplicados na tabela atual
        if current_table_data:
            self._check_duplicate_in_table(
                validated_num, current_table_data, exclude_row, result
            )

        # 3. Verificar duplicados no mês atual (se repository disponível)
        if self._repository and mes is not None and ano is not None:
            self._check_duplicate_in_month(validated_num, mes, ano, result)

        # 4. Verificar duplicados no histórico completo
        if self._repository:
            self._check_duplicate_in_history(validated_num, mes, ano, result)

        return result

    def _validate_numeric(
        self, recibo_num: int | str, result: ReciboValidationResult
    ) -> int | None:
        """Valida se recibo é número inteiro positivo."""
        if recibo_num is None or recibo_num == "":
            result.is_numeric = False
            result.add_error("Recibo não pode ser vazio")
            return None

        # Se já é int, validar range
        if isinstance(recibo_num, int):
            if recibo_num <= 0:
                result.is_numeric = False
                result.add_error(f"Recibo deve ser positivo (recebido: {recibo_num})")
                return None
            return recibo_num

        # Converter string para int
        if not isinstance(recibo_num, str):
            result.is_numeric = False
            result.add_error(f"Tipo inválido: {type(recibo_num).__name__}")
            return None

        try:
            num = int(recibo_num.strip())
            if num <= 0:
                result.is_numeric = False
                result.add_error(f"Recibo deve ser positivo (recebido: {num})")
                return None
            return num
        except ValueError:
            result.is_numeric = False
            result.add_error(f"Recibo inválido: '{recibo_num}'. Deve ser número inteiro.")
            return None

    def _check_duplicate_in_table(
        self,
        recibo_num: int,
        table_data: list[dict[str, Any]],
        exclude_row: int | None,
        result: ReciboValidationResult,
    ) -> None:
        """Verifica se recibo está duplicado na tabela atual."""
        occurrences = 0

        for i, row in enumerate(table_data):
            # Pular linha sendo editada
            if exclude_row is not None and i == exclude_row:
                continue

            row_recibo = row.get("Recibo")
            if row_recibo is None:
                continue

            try:
                row_recibo_num = int(str(row_recibo).strip())
                if row_recibo_num == recibo_num:
                    occurrences += 1
            except (ValueError, AttributeError):
                continue

        if occurrences > 0:
            result.is_duplicate_in_table = True
            result.duplicate_locations.append("Tabela")
            result.add_error(
                f"Recibo {recibo_num} duplicado na tabela ({occurrences}x)"
            )

    def _check_duplicate_in_month(
        self,
        recibo_num: int,
        mes: int,
        ano: int,
        result: ReciboValidationResult,
    ) -> None:
        """Verifica se recibo existe no mês atual na BD."""
        try:
            # Buscar mapa do mês
            mapa = self._repository.buscar_por_mes_ano(mes, ano)
            if not mapa:
                return

            # Verificar linhas do mapa
            for linha in mapa.linhas:
                # Verificar se recibo está no range desta linha
                if linha.recibo_inicio <= recibo_num <= linha.recibo_fim:
                    result.is_duplicate_in_month = True
                    if "Mês Atual" not in result.duplicate_locations:
                        result.duplicate_locations.append("Mês Atual")
                    result.add_error(
                        f"Recibo {recibo_num} já existe no mês {mes}/{ano} (dia {linha.dia})"
                    )
                    break

        except Exception as e:
            logger.error(f"Erro ao verificar duplicado no mês: {e}")
            result.add_warning(f"Não foi possível verificar duplicados no mês: {e}")

    def _check_duplicate_in_history(
        self,
        recibo_num: int,
        current_mes: int | None,
        current_ano: int | None,
        result: ReciboValidationResult,
    ) -> None:
        """Verifica se recibo existe no histórico completo da BD."""
        try:
            # Buscar todos os mapas
            all_mapas = self._repository.buscar_todos()

            for mapa in all_mapas:
                # Pular mês atual (já verificado)
                if current_mes and current_ano:
                    if mapa.mes == current_mes and mapa.ano == current_ano:
                        continue

                # Verificar linhas
                for linha in mapa.linhas:
                    if linha.recibo_inicio <= recibo_num <= linha.recibo_fim:
                        result.is_duplicate_in_history = True
                        if "Histórico" not in result.duplicate_locations:
                            result.duplicate_locations.append("Histórico")
                        result.add_error(
                            f"Recibo {recibo_num} já existe no histórico "
                            f"({mapa.mes}/{mapa.ano}, dia {linha.dia})"
                        )
                        return  # Encontrou, parar busca

        except Exception as e:
            logger.error(f"Erro ao verificar duplicado no histórico: {e}")
            result.add_warning(
                f"Não foi possível verificar duplicados no histórico: {e}"
            )


def validate_recibo_number(
    recibo_num: int | str,
    current_table_data: list[dict[str, Any]] | None = None,
    repository: MapaAssiduidadeRepository | None = None,
    mes: int | None = None,
    ano: int | None = None,
) -> dict[str, Any]:
    """Função de conveniência para validar número de recibo.

    Args:
        recibo_num: Número do recibo
        current_table_data: Dados da tabela atual
        repository: Repository para verificar BD
        mes: Mês atual
        ano: Ano atual

    Returns:
        Dicionário com resultado da validação
    """
    validator = ReciboValidator(repository)
    result = validator.validate_recibo(
        recibo_num=recibo_num,
        current_table_data=current_table_data,
        mes=mes,
        ano=ano,
    )

    return {
        "valido": result.is_valid,
        "recibo": result.recibo_num,
        "numerico": result.is_numeric,
        "duplicado_tabela": result.is_duplicate_in_table,
        "duplicado_mes": result.is_duplicate_in_month,
        "duplicado_historico": result.is_duplicate_in_history,
        "locais_duplicados": result.duplicate_locations,
        "erros": result.errors,
        "avisos": result.warnings,
    }
