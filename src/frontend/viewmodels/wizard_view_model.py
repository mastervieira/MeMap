"""ViewModel para o Wizard guiado de importação.

Gerencia:
- Navegação entre páginas
- Validação de dados do formulário
- Cálculo de resumo financeiro
- Estado do documento (rascunho/fechado)
- Dados do formulário
"""

from __future__ import annotations

import asyncio
import logging
from decimal import Decimal
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import QDate, Signal

from db.models.mapas import MapaAssiduidadeLinha
from src.common.constants.enums import TipoDiaAssiduidade
from src.common.normalizers import decimal_to_float
from src.common.validators.form_validator import ValidationResult
from src.db.models.base_mixin import EstadoDocumento
from src.db.models.mapas import MapaAssiduidade
from src.frontend.viewmodels.base_view_model import BaseViewModel
from src.frontend.views.wizard_logic import WizardValidator

if TYPE_CHECKING:
    from src.repositories.assiduidade_repository import MapaAssiduidadeRepository

logger: logging.Logger = logging.getLogger(__name__)


class WizardViewModel(BaseViewModel):
    """ViewModel para o Wizard guiado de importação."""

    # Signals de navegação
    current_page_changed = Signal(int)
    page_data_updated = Signal(dict)
    validation_error = Signal(str)

    # NOVOS signals para gestão de dados
    resumo_updated = Signal(float, float)  # premio, gastos
    document_state_changed = Signal(object)  # EstadoDocumento
    loading_progress = Signal(int)  # 0-100
    data_loaded = Signal(QDate)  # Quando dados forem carregados

    # FASE 1.2: Signals para persistência e estados
    day_saved = Signal(QDate, bool)  # date, success
    data_modified = Signal(bool)  # has_changes

    def __init__(self) -> None:
        """Inicializa o WizardViewModel."""
        super().__init__()
        self._current_page: int = 0
        self._form_data: dict[str, Any] = {}
        self._table_data: list[dict[str, float]] = []
        self._validator = WizardValidator()
        self._current_state: EstadoDocumento = EstadoDocumento.RASCUNHO
        self._current_date: QDate | None = None
        self._is_loading: bool = False

        # Dados do resumo financeiro
        self._premio: float = 0.0
        self._gastos: float = 0.0

        # FASE 1.2: Gestão de estados de persistência
        self._has_unsaved_changes: bool = False
        self._saved_days: set[tuple[int, int, int]] = set()  # {(year, month, day)}
        self._repository: MapaAssiduidadeRepository | None = None  # Será injetado posteriormente

    def on_appear(self) -> None:
        """Chamado quando o Wizard é ativado."""
        logger.info("Wizard apareceu na tela")

    # ==================== NAVEGAÇÃO ====================

    def go_next(self) -> None:
        """Avança se validação passar (Template Method)."""
        # 1️⃣ Validar página actual
        if not self._validate_current_page():
            self.validation_error.emit(
                f"Página {self._current_page} inválida"
            )
            return

        # 2️⃣ Se passou, avançar
        if self._current_page < 1:
            self._current_page += 1
            self.current_page_changed.emit(self._current_page)
            logger.info(f"Navegando para página {self._current_page}")

    def go_back(self) -> None:
        """Volta para a página anterior."""
        if self._current_page > 0:
            self._current_page -= 1
            self.current_page_changed.emit(self._current_page)
            logger.info(f"Navegando para página {self._current_page}")

    def go_to_page(self, page_number: int) -> None:
        """Vai para uma página específica."""
        if 0 <= page_number <= 1:
            self._current_page = page_number
            self.current_page_changed.emit(self._current_page)
            logger.info(f"Navegando para página {self._current_page}")

    def _validate_current_page(self) -> bool:
        """Validar página actual (override em subclasses)."""
        return True  # Default: sem validação

    # ==================== GESTÃO DE DADOS ====================

    def set_form_field(self, field: str, value: Any) -> None:
        """Define valor de um campo do formulário.

        Args:
            field: Nome do campo
            value: Valor a definir
        """
        self._form_data[field] = value
        self.page_data_updated.emit(self._form_data.copy())
        logger.debug(f"Campo '{field}' atualizado: {value}")

    def get_form_field(self, field: str, default: Any = None) -> Any:
        """Obtém valor de um campo do formulário.

        Args:
            field: Nome do campo
            default: Valor padrão se não existir

        Returns:
            Valor do campo ou default
        """
        return self._form_data.get(field, default)

    def get_form_data(self) -> dict[str, Any]:
        """Retorna cópia dos dados do formulário."""
        return self._form_data.copy()

    def set_table_data(self, table_data: list[dict[str, float]]) -> None:
        """Define dados da tabela de recibos.

        Args:
            table_data: Lista de dicionários com dados dos recibos
        """
        self._table_data = table_data
        logger.debug(f"Dados da tabela atualizados: {len(table_data)} recibos")

    def get_table_data(self) -> list[dict[str, float]]:
        """Retorna dados da tabela de recibos."""
        return self._table_data.copy()

    # ==================== VALIDAÇÃO ====================

    def validate_page_1(self) -> ValidationResult:
        """Valida dados da página 1 usando WizardValidator.

        Returns:
            ValidationResult com dados limpos ou erro
        """
        result = self._validator.validate_page_1(self._form_data)

        if not result.is_valid:
            self.validation_error.emit(result.error_message or "Erro de validação")
            logger.warning(f"Validação falhou: {result.error_message}")
        else:
            logger.info("Validação da página 1 passou")

        return result

    # ==================== RESUMO FINANCEIRO ====================

    def calculate_resumo_financeiro(self) -> tuple[float, float]:
        """Calcula prémio e gastos baseado em dados do formulário.

        Returns:
            Tupla (premio, gastos)
        """
        # TODO: Implementar lógica de cálculo real baseada nos recibos
        # Por enquanto retorna valores simulados

        premio = 0.0
        gastos = 0.0

        # Soma valores dos recibos da tabela
        for recibo in self._table_data:
            # Exemplo: soma colunas como prémio
            # Na implementação real, precisa de lógica de negócio correta
            pass

        self._premio = premio
        self._gastos = gastos

        self.resumo_updated.emit(premio, gastos)
        logger.debug(f"Resumo calculado: Prémio={premio}, Gastos={gastos}")

        return premio, gastos

    def get_resumo(self) -> tuple[float, float]:
        """Retorna resumo financeiro atual.

        Returns:
            Tupla (premio, gastos)
        """
        return self._premio, self._gastos

    # ==================== ESTADO DO DOCUMENTO ====================

    def set_document_state(self, state: EstadoDocumento) -> None:
        """Define estado do documento.

        Args:
            state: Novo estado (RASCUNHO, FECHADO, etc)
        """
        if self._current_state != state:
            self._current_state = state
            self.document_state_changed.emit(state)
            logger.info(f"Estado do documento mudou para: {state.name}")

    def get_document_state(self) -> EstadoDocumento:
        """Retorna estado atual do documento."""
        return self._current_state

    def is_editable(self) -> bool:
        """Verifica se documento é editável.

        Returns:
            True se estado é RASCUNHO, False caso contrário
        """
        return self._current_state == EstadoDocumento.RASCUNHO

    # ==================== CARREGAMENTO ASSÍNCRONO ====================

    async def load_data_for_date(self, date: QDate) -> bool:
        """Carrega dados da base de dados para uma data específica.

        Args:
            date: Data para carregar

        Returns:
            True se carregamento foi bem-sucedido
        """
        if self._is_loading:
            logger.warning("Carregamento já em curso, ignorando nova requisição")
            return False

        self._is_loading = True
        self._current_date = date
        self.loading_progress.emit(10)

        try:
            # TODO: Implementar carregamento real da DB
            # Por enquanto simulação

            # Simula latência
            for i in range(1, 11):
                await asyncio.sleep(0.1)
                self.loading_progress.emit(10 + (i * 8))

            # Simula lógica de estado baseada no dia
            if date.day() % 2 == 0:
                self.set_document_state(EstadoDocumento.RASCUNHO)
            else:
                self.set_document_state(EstadoDocumento.FECHADO)

            self.loading_progress.emit(100)
            self.data_loaded.emit(date)
            logger.info(f"Dados carregados para {date.toString('dd/MM/yyyy')}")

            return True

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            self.validation_error.emit(f"Erro ao carregar dados: {str(e)}")
            return False

        finally:
            self._is_loading = False
            # Aguarda um pouco antes de esconder progresso
            await asyncio.sleep(0.5)
            self.loading_progress.emit(0)

    def get_current_date(self) -> QDate | None:
        """Retorna data atualmente selecionada."""
        return self._current_date

    # ==================== FASE 1.2: PERSISTÊNCIA E ESTADOS ====================

    def set_repository(self, repository) -> None:
        """Injeta repository para persistência.

        Args:
            repository: MapaAssiduidadeRepository para salvar dados
        """
        self._repository = repository
        logger.debug("Repository injetado no WizardViewModel")

    def mark_as_modified(self) -> None:
        """Marca dia como modificado (não salvo)."""
        if not self._has_unsaved_changes:
            self._has_unsaved_changes = True
            self.data_modified.emit(True)
            logger.debug("Dia marcado como modificado")

    def mark_day_as_saved(self, date: QDate) -> None:
        """Marca dia como salvo.

        Args:
            date: Data do dia salvo
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())
        self._saved_days.add(key)
        self._has_unsaved_changes = False
        self.data_modified.emit(False)
        self.day_saved.emit(date, True)
        logger.info(f"Dia {date.toString('dd/MM/yyyy')} marcado como salvo")

    def is_day_saved(self, date: QDate) -> bool:
        """Verifica se dia está salvo.

        Args:
            date: Data a verificar

        Returns:
            True se dia está salvo na BD
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())
        return key in self._saved_days

    def has_unsaved_changes(self) -> bool:
        """Verifica se há mudanças não salvas.

        Returns:
            True se há mudanças não salvas
        """
        return self._has_unsaved_changes

    async def save_current_day(self, date: QDate) -> tuple[bool, str]:
        """Salva dia atual na BD mantendo estado RASCUNHO.

        Args:
            date: Data do dia a salvar

        Returns:
            (sucesso, mensagem)
        """
        logger.info(f"🔵 DEBUG: SAVE_START para {date.toString('dd/MM/yyyy')}")

        if not self._repository:
            logger.error("🔴 DEBUG: Repository NÃO inicializado!")
            return (False, "Repository não inicializado")

        logger.info(f"🔵 DEBUG: Repository OK, sessão: {self._repository.session}")

        try:
            # 1. Validar dados do formulário (Página 1)
            logger.info("🔵 DEBUG: STEP 1 - Validando formulário...")
            logger.info(f"🔵 DEBUG: Form data: {self._form_data}")
            validation_result: ValidationResult = self.validate_page_1()
            if not validation_result.is_valid:
                logger.error(f"🔴 DEBUG: Validação FALHOU: {validation_result.error_message}")
                return (False, validation_result.error_message or "Dados inválidos")

            logger.info("✅ DEBUG: Validação OK")

            # 2. Obter dados da tabela e filtrar linhas vazias
            logger.info("🔵 DEBUG: STEP 2 - Obtendo dados da tabela...")
            table_data: list[dict[str, float]] = self.get_table_data()
            logger.info(f"🔵 DEBUG: Total de linhas na tabela: {len(table_data)}")

            non_empty_rows: list[dict[str, float]] = [
                row for row in table_data
                if self._is_row_non_empty(row)
            ]

            logger.info(f"🔵 DEBUG: Linhas não vazias: {len(non_empty_rows)}")
            if not non_empty_rows:
                logger.error("🔴 DEBUG: NENHUMA linha com dados válidos!")
                return (False, "Nenhum dado para salvar na tabela")

            # 3. Buscar ou criar MapaAssiduidade para o mês
            logger.info("🔵 DEBUG: STEP 3 - Buscando/criando mapa...")
            mes: int = date.month()
            ano: int = date.year()
            dia: int = date.day()

            logger.info(f"🔵 DEBUG: Buscando mapa para {mes}/{ano}...")
            mapa: MapaAssiduidade | None = self._repository.buscar_por_mes_ano(mes, ano)

            if not mapa:
                # Criar novo mapa do mês
                logger.info(f"🔵 DEBUG: Mapa NÃO existe. Criando novo para {mes}/{ano}")
                mapa = self._repository.criar(
                    mes=mes,
                    ano=ano,
                    estado=EstadoDocumento.RASCUNHO,
                    wizard_data=self._form_data
                )
                logger.info(f"✅ DEBUG: Mapa criado com ID={mapa.id}")
            else:
                logger.info(f"✅ DEBUG: Mapa encontrado com ID={mapa.id}")

            # 4. Calcular valores agregados dos recibos

            # Números de recibos
            recibos: list[int] = [
                int(row.get("Recibo", 0))
                for row in non_empty_rows
                if row.get("Recibo")
            ]
            recibo_inicio: int = min(recibos) if recibos else 0
            recibo_fim: int = max(recibos) if recibos else 0

            # Somar valores totais
            total_ips: int = sum(
                int(row.get("Nº IP's", 0))
                for row in non_empty_rows
            )

            total_km: float = sum(
                decimal_to_float(row.get("Km", "0"))
                for row in non_empty_rows
            )

            # Somar valores por distrito
            total_valor: float = sum(
                decimal_to_float(row.get("Setúbal", "0")) +
                decimal_to_float(row.get("Santarém", "0")) +
                decimal_to_float(row.get("Évora", "0"))
                for row in non_empty_rows
            )

            # Obter dia da semana em português
            day_names: dict[int, str] = {
                1: "Segunda",
                2: "Terça",
                3: "Quarta",
                4: "Quinta",
                5: "Sexta",
                6: "Sábado",
                7: "Domingo"
            }
            dia_semana: str = day_names.get(date.dayOfWeek(), "")

            # Locais (zonas)
            zona_primaria: str  = self.get_form_field("zona_primaria", "")
            zona_secundaria: str  = self.get_form_field("zona_secundaria", "")
            locais: str = f"{zona_primaria}/{zona_secundaria}" \
                if zona_secundaria else zona_primaria

            # 5. Adicionar dia ao mapa
            # TODO: Verificar se dia já existe e atualizar em vez de criar novo
            logger.info(f"🔵 DEBUG: STEP 5 - Adicionando dia {dia} ao mapa {mapa.id}")
            logger.info(f"🔵 DEBUG: Recibos: {recibo_inicio}-{recibo_fim}, \
                        IPs: {total_ips}, Km: {total_km}, Valor: {total_valor}")

            linha = self._repository.adicionar_dia(
                mapa_id=mapa.id,
                dia=dia,
                dia_semana=dia_semana,
                tipo=TipoDiaAssiduidade.TRABALHO,
                recibo_inicio=recibo_inicio,
                recibo_fim=recibo_fim,
                ips=total_ips,
                valor_sem_iva=Decimal(str(total_valor)),
                km=Decimal(str(total_km)),
                locais=locais,
                observacoes=None
            )
            logger.info(f"✅ DEBUG: Linha criada com ID={linha.id}")

            # 6. Recalcular totais do mapa
            logger.info("🔵 DEBUG: STEP 6 - Recalculando totais...")
            self._repository.recalcular_totais(mapa.id)
            logger.info("✅ DEBUG: Totais recalculados")

            # 7. Commit das mudanças na BD
            logger.info("🔵 DEBUG: STEP 7 - Fazendo COMMIT na BD...")
            self._repository.session.commit()
            logger.info("✅✅✅ DEBUG: COMMIT REALIZADO COM SUCESSO! ✅✅✅")

            # 8. Marcar dia como salvo
            logger.info("🔵 DEBUG: STEP 8 - Marcando dia como salvo...")
            self.mark_day_as_saved(date)

            mensagem = f"Dia {date.toString('dd/MM/yyyy')} salvo com sucesso"
            logger.info(f"🎉 DEBUG: SALVAMENTO COMPLETO: {mensagem}")
            return (True, mensagem)

        except Exception as e:
            logger.error(f"🔴🔴🔴 DEBUG: ERRO CRÍTICO AO SALVAR: {e}", exc_info=True)
            return (False, f"Erro ao salvar: {str(e)}")

    def _is_row_non_empty(self, row: dict[str, Any]) -> bool:
        """Verifica se linha tem dados válidos.

        Uma linha é considerada vazia se todos os campos numéricos
        são "0" ou vazios.

        Args:
            row: Dados da linha

        Returns:
            True se linha tem dados válidos
        """
        # Colunas numéricas a verificar (exceto Recibo)
        numeric_columns: list[str] = ["Setúbal", "Santarém", "Évora", "Nº IP's", "Km"]

        for col in numeric_columns:
            value = row.get(col, "0")
            # Considera não vazia se valor diferente de "0" ou "0,00"
            if value and value != "0" and value != "0,00":
                return True

        return False

    async def load_day_data(self, date: QDate) -> tuple[bool, str]:
        """Carrega dados de um dia salvo na BD.

        Args:
            date: Data do dia a carregar

        Returns:
            (sucesso, mensagem)
        """
        if not self._repository:
            return (False, "Repository não inicializado")

        try:
            mes: int = date.month()
            ano: int = date.year()
            dia: int = date.day()

            # 1. Buscar mapa do mês
            mapa: MapaAssiduidade | None = self._repository.buscar_por_mes_ano(mes, ano)
            if not mapa:
                return (False, f"Nenhum mapa encontrado para {mes}/{ano}")

            # 2. Buscar linha do dia específico
            linha = None
            for linha_item in mapa.linhas:
                if linha_item.dia == dia:
                    linha: MapaAssiduidadeLinha | None = linha_item
                    break

            if not linha:
                return (False, f"Dia {dia} não encontrado no mapa")

            # 3. Carregar dados do formulário (wizard_data)
            if mapa.wizard_data:
                self._form_data = mapa.wizard_data.copy()
                logger.info(f"Dados do formulário carregados para {dia}/{mes}/{ano}")

            # 4. Reconstruir dados da tabela a partir da linha
            # Precisa de lógica para expandir linha agregada em linhas individuais
            # Por enquanto, vamos criar linhas básicas com os totais
            # TODO: Melhorar para carregar dados detalhados se disponível

            table_data = []

            # Verificar valores não-nulos
            recibo_inicio: int = linha.recibo_inicio or 0
            recibo_fim: int = linha.recibo_fim or 0
            valor_sem_iva: Decimal = linha.valor_sem_iva or Decimal(0)
            km: Decimal = linha.km or Decimal(0)
            ips: int = linha.ips or 0

            # Criar linhas de recibo baseado no range
            num_recibos = recibo_fim - recibo_inicio + 1

            # Dividir valores totais igualmente entre recibos (simplificação)
            valor_por_recibo: float = float(valor_sem_iva) / num_recibos if num_recibos > 0 else 0.0
            km_por_recibo: float = float(km) / num_recibos if num_recibos > 0 else 0.0
            ips_por_recibo: int = ips // num_recibos if num_recibos > 0 else 0

            for i in range(num_recibos):
                recibo_num: int = recibo_inicio + i
                row: dict[str, str | int | dict[str, str | bool]] = {
                    "Recibo": str(recibo_num),
                    "Setúbal": f"{valor_por_recibo:.2f}".replace(".", ","),
                    "Santarém": "0,00",
                    "Évora": "0,00",
                    "Nº IP's": str(ips_por_recibo),
                    "Km": f"{km_por_recibo:.2f}".replace(".", ","),
                    "Partilhado": {
                        "partilhado": False,
                        "tecnico_20": "",
                        "tecnico_30": "",
                    }
                }
                table_data.append(row)

            self._table_data = table_data

            # 5. Marcar como salvo e sem mudanças
            self.mark_day_as_saved(date)
            self._has_unsaved_changes = False

            # 6. Emitir signal de dados carregados
            self.data_loaded.emit(date)

            mensagem = f"Dia {date.toString('dd/MM/yyyy')} carregado com sucesso ({num_recibos} recibos)"
            logger.info(mensagem)
            return (True, mensagem)

        except Exception as e:
            logger.error(f"Erro ao carregar dia: {e}", exc_info=True)
            return (False, f"Erro ao carregar: {str(e)}")

    # ==================== LIFECYCLE ====================

    def dispose(self) -> None:
        """Limpa recursos do Wizard."""
        self._form_data.clear()
        self._table_data.clear()
        self._premio = 0.0
        self._gastos = 0.0
        logger.info("Wizard foi fechado e recursos limpos")
