"""
ViewModel para a tabela de recibos.

Gerencia a lógica de negócio da tabela:
- Validação de dados
- Normalização de valores
- Cálculo de totais
- Estrutura de dados interna
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Signal

from src.common.constants import (
    DEFAULT_CELL_VALUE,
    NUMERIC_COLUMNS,
    RECIBOS_TABLE_COLUMNS,
    ReciboColumn,
)
from src.common.normalizers import (
    decimal_to_float,
    format_currency,
    normalize_decimal,
)
from src.common.utils.validation import validate_positive_int, validate_positive_number
from src.common.validators import ReciboValidator
from src.frontend.viewmodels.base_view_model import BaseViewModel

if TYPE_CHECKING:
    from src.repositories.assiduidade_repository import MapaAssiduidadeRepository

logger: logging.Logger = logging.getLogger(__name__)


class RecibosTableViewModel(BaseViewModel):
    """ViewModel para gerenciar dados da tabela de recibos.

    Responsabilidades:
    - Gerenciar estrutura de dados dos recibos
    - Validar e normalizar valores de entrada
    - Calcular totais automaticamente
    - Notificar View sobre mudanças de dados
    """

    # Sinais
    data_changed = Signal()
    totals_updated = Signal(dict)  # {col_name: float}
    validation_error = Signal(str, int, int)  # mensagem, row, col
    table_rebuilt = Signal(int, int, int)  # quantidade, inicio, fim
    servico_interno_changed = Signal(bool)  # Estado de Serviço Interno mudou
    recibo_sequence_updated = Signal(int, list)  # start_row, new_values
    row_added = Signal(int, dict)  # row_index, row_data
    recibo_validation_changed = Signal(int, bool)  # row, is_valid (para cor vermelha)

    def __init__(self) -> None:
        """Inicializa o ViewModel."""
        super().__init__()
        self._data: list[dict[str, Any]] = []
        self._totals: dict[str, float] = {}
        self._quantidade: int = 0
        self._recibo_inicio: int = 0
        self._recibo_fim: int = 0
        self._servico_interno: bool = False
        self._repository: MapaAssiduidadeRepository | None = None
        self._recibo_validator: ReciboValidator | None = None
        self._current_mes: int | None = None
        self._current_ano: int | None = None

    def on_appear(self) -> None:
        """Chamado quando a View é ativada."""
        logger.info("RecibosTableViewModel apareceu na tela")

    def dispose(self) -> None:
        """Limpa recursos."""
        logger.info("RecibosTableViewModel foi descartado")
        self._data.clear()
        self._totals.clear()

    def set_repository(self, repository: MapaAssiduidadeRepository) -> None:
        """Injeta repository para validação de recibos duplicados.

        Args:
            repository: Repository de assiduidade
        """
        self._repository = repository
        self._recibo_validator = ReciboValidator(repository)
        logger.info("Repository injetado no RecibosTableViewModel")

    def set_current_date(self, mes: int, ano: int) -> None:
        """Define mês/ano atual para validação de recibos.

        Args:
            mes: Mês atual (1-12)
            ano: Ano atual
        """
        self._current_mes = mes
        self._current_ano = ano
        logger.info(f"Data atual definida: {mes}/{ano}")

    def rebuild_data(
            self, quantidade: int,
            recibo_inicio: int,
            recibo_fim: int
            ) -> None:
        """Reconstrói estrutura de dados com novo conjunto de recibos.

        Args:
            quantidade: Número de recibos
            recibo_inicio: Número do primeiro re cibo
            recibo_fim: Número do último recibo
        """
        self._quantidade = quantidade
        self._recibo_inicio = recibo_inicio
        self._recibo_fim = recibo_fim

        # Limpa dados antigos
        self._data.clear()

        # Cria estrutura de dados para cada recibo
        for i in range(quantidade):
            recibo_num: int = recibo_inicio + i
            recibo_data: dict[str, Any] = {
                "Recibo": str(recibo_num),
            }

            # Inicializa colunas numéricas com valor padrão
            for col_name in RECIBOS_TABLE_COLUMNS:
                if col_name not in recibo_data and col_name != "Partilhado":
                    recibo_data[col_name] = DEFAULT_CELL_VALUE

            # Inicializa coluna Partilhado
            recibo_data["Partilhado"] = {
                "partilhado": False,
                "tecnico_20": "",
                "tecnico_30": "",
            }

            self._data.append(recibo_data)

        # Recalcula totais
        self._calculate_totals()

        # Emite sinal
        self.table_rebuilt.emit(quantidade, recibo_inicio, recibo_fim)
        self.data_changed.emit()
        logger.info(f"Tabela reconstruída: {quantidade} \
                    recibos ({recibo_inicio}-{recibo_fim})")

    def set_cell_value(self, row: int, col_name: str, value: str) -> bool:
        """Define valor de uma célula com validação e normalização.

        Args:
            row: Índice da linha
            col_name: Nome da coluna
            value: Valor a ser definido

        Returns:
            True se o valor foi aceito, False se foi rejeitado
        """
        # Verifica limites
        if row < 0 or row >= len(self._data):
            logger.warning(f"Tentativa de acessar linha inválida: {row}")
            return False

        if col_name not in RECIBOS_TABLE_COLUMNS:
            logger.warning(f"Tentativa de acessar coluna inválida: {col_name}")
            return False

        # Obtém índice da coluna
        col_index: int = RECIBOS_TABLE_COLUMNS.index(col_name)

        # FASE 5: Coluna Recibo é editável com auto-incremento
        if col_index == ReciboColumn.RECIBO:
            return self._handle_recibo_edit(row, value)

        # Coluna Partilhado é tratada separadamente
        if col_index == ReciboColumn.PARTILHADO:
            return False  # Widget customizado não passa por aqui

        # Valida e normaliza valor numérico
        if col_index in NUMERIC_COLUMNS:
            if not value.strip():
                # Valor vazio -> usa padrão
                normalized_value: str = DEFAULT_CELL_VALUE
            else:
                # Normaliza (ponto → vírgula)
                normalized_value = normalize_decimal(value)

                # Valida
                if not validate_positive_number(normalized_value):
                    # Valor inválido -> reverte para padrão
                    self.validation_error.emit(
                        f"Valor inválido: '{value}'. Deve ser um número positivo.",
                        row,
                        col_index
                    )
                    normalized_value = DEFAULT_CELL_VALUE

            # Atualiza modelo interno
            self._data[row][col_name] = normalized_value

            # Recalcula totais
            self._calculate_totals()

            # Emite sinal
            self.data_changed.emit()
            return True

        return False

    def set_partilhado_data(
            self, row: int,
            partilhado_data: dict[str, Any]
            ) -> None:
        """Define dados da coluna Partilhado.

        Args:
            row: Índice da linha
            partilhado_data: Dicionário com dados de partilha
        """
        if 0 <= row < len(self._data):
            self._data[row]["Partilhado"] = partilhado_data
            self._calculate_totals()
            self.data_changed.emit()

    def _calculate_totals(self) -> None:
        """Calcula totais de todas as colunas numéricas."""
        self._totals.clear()

        # Para cada coluna numérica (exceto Recibo)
        for col_name in RECIBOS_TABLE_COLUMNS:
            col_index: int = RECIBOS_TABLE_COLUMNS.index(col_name)

            if col_index in NUMERIC_COLUMNS and col_index != ReciboColumn.RECIBO:
                total = 0.0

                # Soma valores de todas as linhas
                for row_data in self._data:
                    value_str = row_data.get(col_name, DEFAULT_CELL_VALUE)
                    try:
                        value: float = decimal_to_float(value_str)
                        total += value
                    except ValueError:
                        # Ignora valores inválidos
                        continue

                self._totals[col_name] = total

        # Emite sinal com totais atualizados
        self.totals_updated.emit(self._totals)
        logger.debug(f"Totais calculados: {self._totals}")

    def get_totals(self) -> dict[str, float]:
        """Retorna totais calculados.

        Returns:
            Dicionário com nome da coluna → valor total
        """
        return self._totals.copy()

    def get_formatted_totals(self) -> dict[str, str]:
        """Retorna totais formatados.

        FASE 7: IPs e Km são formatados como números inteiros (sem €),
        outras colunas como moeda.

        Returns:
            Dicionário com nome da coluna → valor formatado
        """
        formatted = {}

        for col_name, total in self._totals.items():
            col_index = RECIBOS_TABLE_COLUMNS.index(col_name)

            # IPs e Km: formato numérico (sem €)
            if col_index in (ReciboColumn.NUM_IPS, ReciboColumn.KM):
                formatted[col_name] = str(int(total))
            else:
                # Outros: formato moeda
                formatted[col_name] = format_currency(total)

        return formatted

    def get_data(self) -> list[dict[str, Any]]:
        """Retorna dados brutos da tabela.

        Returns:
            Lista de dicionários com dados de cada recibo
        """
        return [row.copy() for row in self._data]

    def get_row_data(self, row: int) -> dict[str, Any] | None:
        """Retorna dados de uma linha específica.

        Args:
            row: Índice da linha

        Returns:
            Dicionário com dados da linha ou None se inválido
        """
        if 0 <= row < len(self._data):
            return self._data[row].copy()
        return None

    def get_cell_value(self, row: int, col_name: str) -> str:
        """Retorna valor de uma célula específica.

        Args:
            row: Índice da linha
            col_name: Nome da coluna

        Returns:
            Valor da célula ou string vazia se inválido
        """
        if 0 <= row < len(self._data) and col_name in RECIBOS_TABLE_COLUMNS:
            return str(self._data[row].get(col_name, ""))
        return ""

    def clear_data(self) -> None:
        """Limpa todos os dados da tabela."""
        self._data.clear()
        self._totals.clear()
        self._quantidade = 0
        self._recibo_inicio = 0
        self._recibo_fim = 0
        self.data_changed.emit()
        logger.info("Dados da tabela limpos")

    # ==================== FASE 1.4: FILTRO DE LINHAS VAZIAS ====================

    def filter_empty_rows(self) -> list[dict[str, Any]]:
        """Remove linhas vazias antes de salvar.

        Uma linha é vazia se todos os campos numéricos são "0" ou vazios.

        Returns:
            Lista com apenas linhas que têm dados válidos
        """
        return [
            row for row in self._data
            if self._has_valid_data(row)
        ]

    def _has_valid_data(self, row: dict[str, Any]) -> bool:
        """Verifica se linha tem dados válidos.

        Args:
            row: Dicionário com dados da linha

        Returns:
            True se linha tem pelo menos um campo numérico diferente de zero
        """

        # Verificar colunas numéricas (exceto Recibo)
        for col_name in RECIBOS_TABLE_COLUMNS:
            col_index = RECIBOS_TABLE_COLUMNS.index(col_name)

            # Ignorar coluna Recibo
            if col_index == ReciboColumn.RECIBO:
                continue

            # Verificar se é coluna numérica
            if col_index in NUMERIC_COLUMNS:
                value = row.get(col_name, "0")

                # Considera não vazia se valor diferente de "0" ou "0,00"
                if value and value != "0" and value != "0,00":
                    return True

        return False

    def has_data(self) -> bool:
        """Verifica se há dados válidos na tabela.

        Returns:
            True se há pelo menos uma linha com dados
        """
        return len(self.filter_empty_rows()) > 0

    # ==================== FASE 4: SERVIÇO INTERNO ====================

    def set_servico_interno(self, enabled: bool) -> None:
        """Ativa/desativa modo Serviço Interno.

        FASE 4 (CORRIGIDO): Quando ativado, apenas emite signal.
        A View adiciona linha extra abaixo do cabeçalho.

        Args:
            enabled: True para ativar, False para desativar
        """
        if self._servico_interno == enabled:
            return

        self._servico_interno = enabled

        # Emitir signal (View adiciona/remove linha de serviço interno)
        self.servico_interno_changed.emit(enabled)

        logger.info(f"Modo Serviço Interno: {'ATIVADO' if enabled else 'DESATIVADO'}")

    def is_servico_interno(self) -> bool:
        """Retorna se modo Serviço Interno está ativo.

        Returns:
            True se modo Serviço Interno está ativo
        """
        return self._servico_interno

    def get_servico_interno_km(self) -> float:
        """Retorna valor de Km do Serviço Interno (se ativo).

        FASE 4: Deve ser chamado pela View para obter o valor digitado
        na linha de Serviço Interno.

        Returns:
            Valor de Km digitado na linha de Serviço Interno (0.0 se não ativo)
        """
        # Este valor será definido pela View quando o usuário editar
        # Por enquanto retorna 0.0 (será implementado via signal se necessário)
        return 0.0

    # ==================== FASE 5: RECIBOS EDITÁVEIS ====================

    def _handle_recibo_edit(self, row: int, new_value: str) -> bool:
        """Processa edição da coluna Recibo com auto-incremento e validação.

        1. Valida se é número inteiro positivo
        2. Valida duplicados (tabela, mês, histórico)
        3. Atualiza valor na linha editada
        4. Recalcula incrementos abaixo (+1, +2, ...)
        5. Emite signal de validação (para marcar célula vermelha se inválido)

        Args:
            row: Índice da linha editada
            new_value: Novo valor do recibo

        Returns:
            True se valor foi aceito, False se rejeitado
        """
        if not new_value.strip():
            logger.warning("Valor vazio para Recibo")
            return False

        if not validate_positive_int(new_value):
            logger.warning(f"Valor inválido para Recibo: '{new_value}'")
            self.validation_error.emit(
                f"Recibo inválido: '{new_value}'. Deve ser número inteiro positivo.",
                row,
                ReciboColumn.RECIBO
            )
            self.recibo_validation_changed.emit(row, False)
            return False

        new_recibo = int(new_value)

        # Validar duplicados (se validator disponível)
        if self._recibo_validator:
            validation_result = self._recibo_validator.validate_recibo(
                recibo_num=new_recibo,
                current_table_data=self._data,
                mes=self._current_mes,
                ano=self._current_ano,
                exclude_row=row,  # Excluir própria linha
            )

            if not validation_result.is_valid:
                # Recibo duplicado - emitir erro mas ACEITAR o valor
                error_msg = " | ".join(validation_result.errors)
                logger.warning(f"Recibo {new_recibo} duplicado: {error_msg}")
                self.validation_error.emit(error_msg, row, ReciboColumn.RECIBO)
                self.recibo_validation_changed.emit(row, False)  # Marcar vermelho
                # NÃO retornar False - permitir o valor mas sinalizar erro visual
            else:
                # Recibo válido - limpar marcação vermelha
                self.recibo_validation_changed.emit(row, True)
        else:
            # Sem validator - considerar válido
            self.recibo_validation_changed.emit(row, True)

        # Atualizar linha editada
        self._data[row]["Recibo"] = str(new_recibo)

        # Recalcular sequência abaixo (incremento +1)
        updated_recibos = []
        for i in range(row + 1, len(self._data)):
            expected_recibo = new_recibo + (i - row)
            self._data[i]["Recibo"] = str(expected_recibo)
            updated_recibos.append(str(expected_recibo))

            # Validar cada recibo da sequência também
            if self._recibo_validator:
                seq_validation = self._recibo_validator.validate_recibo(
                    recibo_num=expected_recibo,
                    current_table_data=self._data,
                    mes=self._current_mes,
                    ano=self._current_ano,
                    exclude_row=i,
                )
                self.recibo_validation_changed.emit(i, seq_validation.is_valid)

        # Atualizar recibo_fim
        if len(self._data) > 0:
            self._recibo_fim = int(self._data[-1]["Recibo"])

        # Emitir signal para UI atualizar
        if updated_recibos:
            self.recibo_sequence_updated.emit(row + 1, updated_recibos)

        self.data_changed.emit()
        logger.info(f"Recibo linha {row} editado para {new_recibo}, sequência recalculada")
        return True

    # ==================== FASE 6: ADICIONAR LINHAS ====================

    def add_row(self) -> None:
        """Adiciona nova linha com recibo auto-incrementado.

        FASE 6: Adiciona linha dinamicamente quando usuário pressiona "+" no teclado.
        """
        if not self._data:
            logger.warning("Tabela vazia, não é possível adicionar linha")
            return

        # Calcular próximo número de recibo
        last_recibo = int(self._data[-1]["Recibo"])
        new_recibo: int = last_recibo + 1

        # Criar nova linha
        new_row_data: dict[str, str | dict[str, bool | str]] = {
            "Recibo": str(new_recibo),
            "Partilhado": {
                "partilhado": False,
                "tecnico_20": "",
                "tecnico_30": "",
            }
        }

        # Inicializar colunas numéricas com valor padrão
        for col_name in RECIBOS_TABLE_COLUMNS:
            if col_name not in new_row_data and col_name != "Partilhado":
                new_row_data[col_name] = DEFAULT_CELL_VALUE

        # Adicionar aos dados
        self._data.append(new_row_data)
        self._quantidade += 1
        self._recibo_fim = new_recibo

        # Emitir signals
        new_row_index: int = len(self._data) - 1
        self.row_added.emit(new_row_index, new_row_data)
        self.data_changed.emit()

        logger.info(f"Linha adicionada: Recibo {new_recibo} (total: {self._quantidade} linhas)")

    @property
    def row_count(self) -> int:
        """Retorna número de linhas de dados."""
        return len(self._data)

    @property
    def is_empty(self) -> bool:
        """Verifica se a tabela está vazia."""
        return len(self._data) == 0
