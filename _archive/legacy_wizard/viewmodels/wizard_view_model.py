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
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Signal

from src.common.constants.enums import TipoDiaAssiduidade
from src.common.normalizers import decimal_to_float
from src.common.validators.form_validator import ValidationResult
from src.db.models.base_mixin import EstadoDocumento
from src.db.models.mapas import TabelaTaxas, TabelaTaxasLinha
from src.frontend.viewmodels.base_view_model import BaseViewModel
from src.frontend.views.wizard_logic import WizardValidator

if TYPE_CHECKING:
    from src.repositories.tabela_taxas_repository import TabelaTaxasRepository

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
    saving_progress = Signal(int, str)  # progresso (0-100), mensagem

    def __init__(self) -> None:
        """Inicializa o WizardViewModel."""
        super().__init__()
        self._current_page: int = 0
        self._form_data: dict[str, object] = {}
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
        self._repository: TabelaTaxasRepository | None = None  # Será injetado posteriormente

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

    def set_form_field(self, field: str, value: float) -> None:
        """Define valor de um campo do formulário.

        Args:
            field: Nome do campo
            value: Valor a definir
        """
        self._form_data[field] = value
        self.page_data_updated.emit(self._form_data.copy())
        logger.debug(f"Campo '{field}' atualizado: {value}")

    def get_form_field(self, field: str, default: object = None) -> object:
        """Obtém valor de um campo do formulário.

        Args:
            field: Nome do campo
            default: Valor padrão se não existir

        Returns:
            Valor do campo ou default
        """
        return self._form_data.get(field, default)

    def get_form_data(self) -> dict[str, object]:
        """Retorna cópia dos dados do formulário."""
        return self._form_data.copy()

    def clear_form_data(self) -> None:
        """Limpa todos os dados do formulário.

        Remove todos os campos do formulário, resetando para estado inicial.
        """
        self._form_data.clear()
        logger.info("Dados do formulário limpos")

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
        result: ValidationResult = self._validator.validate_page_1(self._form_data)

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

            # Emitir progresso sem await asyncio.sleep (causa problemas com qasync)
            self.loading_progress.emit(50)

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
            # Esconder progresso imediatamente (sem await asyncio.sleep)
            self.loading_progress.emit(0)

    def get_current_date(self) -> QDate | None:
        """Retorna data atualmente selecionada."""
        return self._current_date

    # ==================== FASE 1.2: PERSISTÊNCIA E ESTADOS ====================

    def set_repository(self, repository: TabelaTaxasRepository) -> None:
        """Injeta repository para persistência.

        Args:
            repository: TabelaTaxasRepository para salvar dados
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

        # Progresso: Iniciar (0%)
        self.saving_progress.emit(0, "Iniciando salvamento...")

        if not self._repository:
            logger.error("🔴 DEBUG: Repository NÃO inicializado!")
            return (False, "Repository não inicializado")

        logger.info(f"🔵 DEBUG: Repository OK, sessão: {self._repository.session}")

        try:
            # 1. Validar dados do formulário (Página 1)
            logger.info("🔵 DEBUG: STEP 1 - Validando formulário...")
            self.saving_progress.emit(10, "Validando formulário...")
            logger.info(f"🔵 DEBUG: Form data: {self._form_data}")
            validation_result: ValidationResult = self.validate_page_1()
            if not validation_result.is_valid:
                logger.error(f"🔴 DEBUG: Validação FALHOU: {validation_result.error_message}")
                return (False, validation_result.error_message or "Dados inválidos")

            logger.info("✅ DEBUG: Validação OK")
            self.saving_progress.emit(20, "Processando dados da tabela...")

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

            # 2.5. CRÍTICO: Verificar duplicados ANTES de salvar
            logger.info("🔵 DEBUG: STEP 2.5 - Verificando recibos duplicados...")
            # IMPORTANTE: Passa dia atual para ignorar recibos do próprio dia
            has_duplicates, duplicate_msg = self._check_duplicate_recibos(
                table_data,
                date.month(),
                date.year(),
                date.day()  # Ignora duplicados do próprio dia
            )
            if has_duplicates:
                logger.error(f"🔴 DEBUG: DUPLICADOS ENCONTRADOS!\n{duplicate_msg}")
                return (False, duplicate_msg)
            logger.info("✅ DEBUG: Nenhum duplicado encontrado")
            self.saving_progress.emit(30, "Preparando base de dados...")

            # 3. Buscar ou criar TabelaTaxas para o mês
            logger.info("🔵 DEBUG: STEP 3 - Buscando/criando mapa...")
            mes: int = date.month()
            ano: int = date.year()
            dia: int = date.day()

            logger.info(f"🔵 DEBUG: Buscando mapa para {mes}/{ano}...")
            mapa: TabelaTaxas | None = self._repository.buscar_por_mes_ano(mes, ano)

            if not mapa:
                # Criar novo mapa do mês
                logger.info(f"🔵 DEBUG: Mapa NÃO existe. Criando novo para {mes}/{ano}")
                # CORRIGIDO: wizard_data como dicionário de dias
                # Estrutura: {"dias": {"13": {"form": {...}, "table": [...]}, "14": {...}}}
                wizard_data_completo: dict[str, object] = {
                    "dias": {
                        str(dia): {
                            "form": self._form_data,
                            "table": table_data
                        }
                    }
                }
                mapa = self._repository.criar(
                    mes=mes,
                    ano=ano,
                    estado=EstadoDocumento.RASCUNHO,
                    wizard_data=wizard_data_completo
                )
                logger.info(f"✅ DEBUG: Mapa criado com ID={mapa.id}, dia {dia} salvo")
            else:
                logger.info(f"✅ DEBUG: Mapa encontrado com ID={mapa.id}")
                # CORRIGIDO: Atualizar apenas o dia específico
                # Inicializar estrutura se não existir
                if not isinstance(mapa.wizard_data, dict):
                    mapa.wizard_data = {"dias": {}}
                if "dias" not in mapa.wizard_data:
                    mapa.wizard_data["dias"] = {}

                # Atualizar dados do dia específico
                mapa.wizard_data["dias"][str(dia)] = {
                    "form": self._form_data,
                    "table": table_data
                }
                logger.info(f"✅ DEBUG: Dia {dia} atualizado no mapa {mapa.id}")

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

            total_km: float= sum(
                decimal_to_float(row.get("Km", "0"))
                for row in non_empty_rows
            )

            # Somar valores por distrito
            total_valor: float = float(sum(
                decimal_to_float(row.get("Setúbal", "0")) +
                decimal_to_float(row.get("Santarém", "0")) +
                decimal_to_float(row.get("Évora", "0"))
                for row in non_empty_rows
            ))

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
            self.saving_progress.emit(50, "Salvando dados do dia...")
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
                valor_com_iva=Decimal(str(total_valor)),
                km=Decimal(str(total_km)),
                locais=locais,
                observacoes=None
            )
            logger.info(f"✅ DEBUG: Linha criada com ID={linha.id}")

            # 6. Atualizar wizard_data com dados detalhados do dia
            self.saving_progress.emit(60, "Guardando detalhes...")
            logger.info("🔵 DEBUG: STEP 6 - Atualizando wizard_data com dados detalhados...")
            if not mapa.wizard_data:
                mapa.wizard_data = {}
            if "dias" not in mapa.wizard_data:
                mapa.wizard_data["dias"] = {}

            # Salvar dados do formulário E da tabela (detalhados)
            # IMPORTANTE: Usar chaves "form" e "table" para compatibilidade com carregamento
            mapa.wizard_data["dias"][str(dia)] = {
                "form": self._form_data.copy(),
                "table": [row.copy() for row in non_empty_rows]
            }

            # CRÍTICO: Marcar wizard_data como modificado para SQLAlchemy persistir
            from sqlalchemy.orm.attributes import flag_modified
            flag_modified(mapa, "wizard_data")
            logger.info(f"✅ DEBUG: wizard_data atualizado com {len(non_empty_rows)} linhas detalhadas")

            # 7. Recalcular totais do mapa
            self.saving_progress.emit(70, "Recalculando totais...")
            logger.info("🔵 DEBUG: STEP 7 - Recalculando totais...")
            self._repository.recalcular_totais(mapa.id)
            logger.info("✅ DEBUG: Totais recalculados")

            # 8. Commit das mudanças na BD
            self.saving_progress.emit(80, "Confirmando alterações...")
            logger.info("🔵 DEBUG: STEP 8 - Fazendo COMMIT na BD...")

            # LOG DETALHADO: Estado ANTES do commit
            logger.info("=" * 100)
            logger.info("📸 SNAPSHOT ANTES DO COMMIT:")
            logger.info("=" * 100)
            logger.info(f"   Mapa ID: {mapa.id}, Mes/Ano: {mapa.mes}/{mapa.ano}")
            logger.info(f"   Número de linhas em mapa.linhas: {len(mapa.linhas)}")
            logger.info(f"   wizard_data['dias'] keys: {list(mapa.wizard_data.get('dias', {}).keys()) if mapa.wizard_data else 'None'}")
            if mapa.wizard_data and "dias" in mapa.wizard_data and str(dia) in mapa.wizard_data["dias"]:
                dados_dia_antes = mapa.wizard_data["dias"][str(dia)]
                logger.info(f"   wizard_data['dias']['{dia}']['form']: {dados_dia_antes.get('form', 'N/A')}")
                logger.info(f"   wizard_data['dias']['{dia}']['table'] ({len(dados_dia_antes.get('table', []))} linhas):")
                for i, row in enumerate(dados_dia_antes.get("table", []), 1):
                    logger.info(f"      Linha {i}: {row}")
            else:
                logger.info(f"   ⚠️  wizard_data['dias']['{dia}'] NÃO EXISTE!")
            logger.info("=" * 100)

            self._repository.session.commit()
            logger.info("✅✅✅ DEBUG: COMMIT REALIZADO COM SUCESSO! ✅✅✅")

            # LOG DETALHADO: Estado DEPOIS do commit (antes do refresh)
            logger.info("=" * 100)
            logger.info("📸 SNAPSHOT DEPOIS DO COMMIT (antes do refresh):")
            logger.info("=" * 100)
            logger.info(f"   Mapa ID: {mapa.id}, Mes/Ano: {mapa.mes}/{mapa.ano}")
            logger.info(f"   Número de linhas em mapa.linhas: {len(mapa.linhas)}")
            logger.info(f"   wizard_data['dias'] keys: {list(mapa.wizard_data.get('dias', {}).keys()) if mapa.wizard_data else 'None'}")
            if mapa.wizard_data and "dias" in mapa.wizard_data and str(dia) in mapa.wizard_data["dias"]:
                dados_dia_depois = mapa.wizard_data["dias"][str(dia)]
                logger.info(f"   wizard_data['dias']['{dia}']['form']: {dados_dia_depois.get('form', 'N/A')}")
                logger.info(f"   wizard_data['dias']['{dia}']['table'] ({len(dados_dia_depois.get('table', []))} linhas):")
                for i, row in enumerate(dados_dia_depois.get("table", []), 1):
                    logger.info(f"      Linha {i}: {row}")
            else:
                logger.info(f"   ⚠️  wizard_data['dias']['{dia}'] NÃO EXISTE!")
            logger.info("=" * 100)

            # 8.5. VERIFICAÇÃO PÓS-COMMIT: Ler dados de volta e comparar
            self.saving_progress.emit(90, "Verificando dados gravados...")
            logger.info("🔵 DEBUG: STEP 8.5 - Verificando dados gravados na BD...")
            logger.info("=" * 80)
            logger.info("📊 COMPARAÇÃO: DADOS INSERIDOS vs DADOS GRAVADOS")
            logger.info("=" * 80)

            # Log dados INSERIDOS pelo usuário
            logger.info(f"📝 DADOS INSERIDOS PELO USUÁRIO:")
            logger.info(f"   Formulário: {self._form_data}")
            logger.info(f"   Tabela ({len(non_empty_rows)} linhas):")
            for i, row in enumerate(non_empty_rows, 1):
                logger.info(f"      Linha {i}: {row}")

            # Fazer refresh do mapa para obter dados da BD
            self._repository.session.refresh(mapa)

            # LOG DETALHADO: Estado DEPOIS do refresh (dados frescos da BD)
            logger.info("=" * 100)
            logger.info("📸 SNAPSHOT DEPOIS DO REFRESH (dados frescos da BD):")
            logger.info("=" * 100)
            logger.info(f"   Mapa ID: {mapa.id}, Mes/Ano: {mapa.mes}/{mapa.ano}")
            logger.info(f"   Número de linhas em mapa.linhas: {len(mapa.linhas)}")
            logger.info(f"   wizard_data type: {type(mapa.wizard_data)}")
            logger.info(f"   wizard_data: {mapa.wizard_data}")
            logger.info(f"   wizard_data['dias'] keys: {list(mapa.wizard_data.get('dias', {}).keys()) if mapa.wizard_data else 'None'}")
            if mapa.wizard_data and "dias" in mapa.wizard_data and str(dia) in mapa.wizard_data["dias"]:
                dados_dia_refresh = mapa.wizard_data["dias"][str(dia)]
                logger.info(f"   wizard_data['dias']['{dia}']['form']: {dados_dia_refresh.get('form', 'N/A')}")
                logger.info(f"   wizard_data['dias']['{dia}']['table'] ({len(dados_dia_refresh.get('table', []))} linhas):")
                for i, row in enumerate(dados_dia_refresh.get("table", []), 1):
                    logger.info(f"      Linha {i}: {row}")
            else:
                logger.info(f"   ⚠️⚠️⚠️  wizard_data['dias']['{dia}'] NÃO EXISTE APÓS REFRESH!")
            logger.info("=" * 100)

            # Verificar linha agregada
            linha_gravada: TabelaTaxasLinha | None = None
            for linha_item in mapa.linhas:
                if linha_item.dia == dia:
                    linha_gravada = linha_item
                    break

            if not linha_gravada:
                logger.error("🔴 ERRO CRÍTICO: Linha não encontrada após commit!")
                return (False, "Erro de verificação: linha não encontrada na BD após commit")

            # Log dados GRAVADOS na BD
            logger.info(f"💾 DADOS GRAVADOS NA BD:")
            logger.info(f"   Linha Agregada:")
            logger.info(f"      ID: {linha_gravada.id}")
            logger.info(f"      Dia: {linha_gravada.dia}")
            logger.info(f"      Recibos: {linha_gravada.recibo_inicio}-{linha_gravada.recibo_fim}")
            logger.info(f"      IPs: {linha_gravada.ips}")
            logger.info(f"      Km: {linha_gravada.km}")
            logger.info(f"      Valor s/ IVA: {linha_gravada.valor_com_iva}")

            # Verificar wizard_data
            dia_key = str(dia)
            if not mapa.wizard_data or "dias" not in mapa.wizard_data or dia_key not in mapa.wizard_data["dias"]:
                logger.error(f"🔴 ERRO CRÍTICO: wizard_data não contém dados do dia {dia}!")
                logger.error(f"   wizard_data atual: {mapa.wizard_data}")
                return (False, f"Erro de verificação: dados detalhados do dia {dia} não foram salvos")

            dados_gravados = mapa.wizard_data["dias"][dia_key]
            logger.info(f"   wizard_data['dias']['{dia_key}']:")
            logger.info(f"      form: {dados_gravados.get('form', {})}")
            logger.info(f"      table ({len(dados_gravados.get('table', []))} linhas):")
            for i, row in enumerate(dados_gravados.get("table", []), 1):
                logger.info(f"         Linha {i}: {row}")

            # Comparar dados
            dados_ok = True
            erros = []

            # Comparar tabela
            if len(dados_gravados.get("table", [])) != len(non_empty_rows):
                dados_ok = False
                erros.append(f"Número de linhas diferente: inserido={len(non_empty_rows)}, gravado={len(dados_gravados.get('table', []))}")

            # Comparar recibos da linha agregada
            if linha_gravada.recibo_inicio != recibo_inicio:
                dados_ok = False
                erros.append(f"Recibo início diferente: inserido={recibo_inicio}, gravado={linha_gravada.recibo_inicio}")

            if linha_gravada.recibo_fim != recibo_fim:
                dados_ok = False
                erros.append(f"Recibo fim diferente: inserido={recibo_fim}, gravado={linha_gravada.recibo_fim}")

            logger.info("=" * 80)
            if dados_ok:
                logger.info("✅ VERIFICAÇÃO: Dados gravados CORRESPONDEM aos dados inseridos!")
            else:
                logger.error("🔴 VERIFICAÇÃO FALHOU: Dados gravados DIFEREM dos dados inseridos!")
                for erro in erros:
                    logger.error(f"   - {erro}")
                logger.error("=" * 80)
                return (False, f"Erro de verificação: {'; '.join(erros)}")
            logger.info("=" * 80)

            # 9. Marcar dia como salvo
            logger.info("🔵 DEBUG: STEP 9 - Marcando dia como salvo...")
            self.mark_day_as_saved(date)

            # Progresso: Concluído (100%)
            self.saving_progress.emit(100, "Salvamento concluído!")

            mensagem = f"Dia {date.toString('dd/MM/yyyy')} salvo com sucesso"
            logger.info(f"🎉 DEBUG: SALVAMENTO COMPLETO: {mensagem}")
            return (True, mensagem)

        except Exception as e:
            logger.error(f"🔴🔴🔴 DEBUG: ERRO CRÍTICO AO SALVAR: {e}", exc_info=True)
            return (False, f"Erro ao salvar: {str(e)}")

    async def delete_current_day(self, date: QDate | None = None) -> tuple[bool, str]:
        """Elimina o dia atual da BD e volta ao estado inicial.

        Remove todos os dados do dia (wizard_data e linha de assiduidade)
        e marca o dia como não salvo. O dia volta ao estado inicial (novo).

        Args:
            date: Data do dia a eliminar (usa _current_date se não fornecida)

        Returns:
            (sucesso, mensagem)
        """
        # Usa data fornecida ou _current_date
        target_date = date if date else self._current_date

        if not target_date:
            return (False, "Nenhuma data selecionada")

        if not self._repository:
            return (False, "Repository não inicializado")

        try:
            mes = target_date.month()
            ano = target_date.year()
            dia = target_date.day()
            date_str = target_date.toString("dd/MM/yyyy")

            logger.info(f"🗑️ Eliminando dia {date_str} da BD...")

            # Progresso: Iniciar (0%)
            self.saving_progress.emit(0, "Iniciando eliminação...")

            # 1. Buscar mapa do mês
            self.saving_progress.emit(20, "Buscando dados...")
            mapa: TabelaTaxas | None = self._repository.buscar_por_mes_ano(mes, ano)

            if mapa:
                # 2. Remover dia do wizard_data
                self.saving_progress.emit(40, "Removendo dados do dia...")
                if isinstance(mapa.wizard_data, dict) and "dias" in mapa.wizard_data:
                    dia_key = str(dia)
                    if dia_key in mapa.wizard_data["dias"]:
                        del mapa.wizard_data["dias"][dia_key]
                        # CRÍTICO: Reatribuir wizard_data para SQLAlchemy detectar a mudança
                        # Modificações in-place em campos JSON não são detectadas automaticamente
                        mapa.wizard_data = mapa.wizard_data
                        logger.info(f"✅ Dia {dia} removido do wizard_data")

                # 3. Remover linha de assiduidade do dia
                self.saving_progress.emit(60, "Eliminando da base de dados...")
                linha_removida = False
                for linha in list(mapa.linhas):  # list() para copiar e evitar modificação durante iteração
                    if linha.dia == dia:
                        self._repository.session.delete(linha)
                        linha_removida = True
                        logger.info(f"✅ Linha de assiduidade do dia {dia} removida")

                # 4. CRÍTICO: Verificar se ainda há linhas de outros dias
                # Fazer flush para atualizar mapa.linhas após os deletes
                self._repository.session.flush()

                # CRÍTICO: Refresh para recarregar mapa.linhas da BD
                # Sem isto, mapa.linhas fica com cache stale e conta linhas deletadas
                self._repository.session.refresh(mapa)

                # Só eliminar o mapa se NÃO houver NENHUMA linha de assiduidade
                if len(mapa.linhas) == 0:
                    self._repository.session.delete(mapa)
                    logger.info(f"✅ Mapa {mes}/{ano} eliminado (sem nenhuma linha de assiduidade)")
                else:
                    # Recalcular totais se mapa ainda tem linhas de outros dias
                    self._repository.recalcular_totais(mapa.id)
                    logger.info(f"✅ Totais do mapa {mes}/{ano} recalculados ({len(mapa.linhas)} linhas restantes)")

                # 5. Commit
                self.saving_progress.emit(80, "Confirmando eliminação...")
                self._repository.session.commit()
                logger.info("✅ Mudanças commitadas na BD")

                # 5.5. VERIFICAÇÃO PÓS-COMMIT: Confirmar que foi eliminado
                self.saving_progress.emit(90, "Verificando eliminação...")
                logger.info("=" * 80)
                logger.info("🔍 VERIFICAÇÃO: Confirmando eliminação na BD...")
                logger.info("=" * 80)

                # Verificar se o mapa ainda existe
                mapa_verificacao = self._repository.buscar_por_mes_ano(mes, ano)

                if mapa_verificacao:
                    # Mapa existe - verificar se dia foi eliminado
                    dia_encontrado = False
                    for linha in mapa_verificacao.linhas:
                        if linha.dia == dia:
                            dia_encontrado = True
                            break

                    if dia_encontrado:
                        logger.error(f"🔴 ERRO: Dia {dia} ainda existe na BD após eliminação!")
                        return (False, f"Erro de verificação: dia {dia} não foi eliminado")

                    # Verificar wizard_data
                    if isinstance(mapa_verificacao.wizard_data, dict) and "dias" in mapa_verificacao.wizard_data:
                        if str(dia) in mapa_verificacao.wizard_data["dias"]:
                            logger.error(f"🔴 ERRO: Dia {dia} ainda existe em wizard_data após eliminação!")
                            return (False, f"Erro de verificação: dados do dia {dia} não foram removidos")

                    logger.info(f"✅ VERIFICAÇÃO: Dia {dia} eliminado com sucesso (mapa {mes}/{ano} ainda tem {len(mapa_verificacao.linhas)} dias)")
                else:
                    logger.info(f"✅ VERIFICAÇÃO: Mapa {mes}/{ano} completamente eliminado (era o último dia)")

                logger.info("=" * 80)

            # 6. Limpar dados do ViewModel
            self._form_data.clear()
            self._table_data.clear()
            self._has_unsaved_changes = False

            # 7. Marcar dia como NÃO salvo (remover do conjunto)
            key = (target_date.year(), target_date.month(), target_date.day())
            self._saved_days.discard(key)

            # 8. Emitir signals
            self.day_saved.emit(target_date, False)  # False = não salvo (eliminado)
            self.data_modified.emit(False)  # Sem mudanças pendentes

            # 9. Progress final
            self.saving_progress.emit(100, "Eliminação concluída!")

            logger.info(f"🎉 Dia {date_str} eliminado da BD e resetado para estado inicial")
            return (True, f"Dia {date_str} eliminado com sucesso")

        except Exception as e:
            logger.error(f"❌ Erro ao eliminar dia: {e}", exc_info=True)
            return (False, f"Erro ao eliminar: {str(e)}")

    def _is_row_non_empty(self, row: dict[str, object]) -> bool:
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

    def _check_duplicate_recibos(
        self,
        table_data: list[dict[str, object]],
        mes: int,
        ano: int,
        dia: int
    ) -> tuple[bool, str]:
        """Verifica se há recibos duplicados antes de salvar.

        CRÍTICO: Ignora recibos do próprio dia sendo editado para permitir
        edição de dias salvos sem falsos positivos.

        Args:
            table_data: Dados da tabela
            mes: Mês atual
            ano: Ano atual
            dia: Dia atual sendo editado (ignora duplicados do próprio dia)

        Returns:
            (tem_duplicados, mensagem_erro)
        """
        if not self._repository:
            return (False, "")

        from src.common.validators import ReciboValidator

        validator = ReciboValidator(self._repository)
        duplicates = []

        for i, row in enumerate(table_data):
            recibo_num_str = row.get("Recibo")
            if not recibo_num_str:
                continue

            try:
                recibo_num = int(recibo_num_str)
            except (ValueError, TypeError):
                continue

            # Validar recibo (passa dia_atual para ignorar recibos do próprio dia)
            validation_result = validator.validate_recibo(
                recibo_num=recibo_num,
                current_table_data=table_data,
                mes=mes,
                ano=ano,
                exclude_row=i,
                dia_atual=dia,  # CRÍTICO: ignora duplicados do próprio dia
            )

            if not validation_result.is_valid:
                duplicates.append(
                    f"  • Linha {i+1}: Recibo {recibo_num}\n"
                    f"    {', '.join(validation_result.errors)}"
                )

        if duplicates:
            error_msg = (
                "❌ IMPOSSÍVEL SALVAR - Recibos duplicados encontrados:\n\n" +
                "\n\n".join(duplicates[:3])  # Máximo 3 erros para não poluir
            )
            if len(duplicates) > 3:
                error_msg += f"\n\n... e mais {len(duplicates) - 3} erro(s)"

            error_msg += "\n\n⚠️ Corrija os recibos duplicados antes de salvar!"
            return (True, error_msg)

        return (False, "")

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
            mapa: TabelaTaxas | None = self._repository.buscar_por_mes_ano(mes, ano)
            if not mapa:
                return (False, f"Nenhum mapa encontrado para {mes}/{ano}")

            # 2. Buscar linha do dia específico
            linha: TabelaTaxasLinha | None = None
            for linha_item in mapa.linhas:
                if linha_item.dia == dia:
                    linha = linha_item
                    break

            if not linha:
                return (False, f"Dia {dia} não encontrado no mapa")

            # 3. Carregar dados do formulário e tabela (wizard_data)
            table_data_loaded: bool = False
            num_recibos: int = 0

            if mapa.wizard_data:
                # CORRIGIDO: Novo formato com dias separados
                # Estrutura: {"dias": {"13": {"form": {...}, "table": [...]}, "14": {...}}}
                if isinstance(mapa.wizard_data, dict) and "dias" in mapa.wizard_data:
                    # Formato novo: dicionário por dia
                    dia_key = str(dia)
                    if dia_key in mapa.wizard_data["dias"]:  # type: ignore
                        dia_data = mapa.wizard_data["dias"][dia_key]  # type: ignore

                        if "form" in dia_data:
                            self._form_data = dict(dia_data["form"])
                            logger.info(f"Dados do formulário carregados (novo formato) para {dia}/{mes}/{ano}")

                        if "table" in dia_data and dia_data["table"]:
                            self._table_data = list(dia_data["table"])
                            table_data_loaded = True
                            num_recibos = len(self._table_data)
                            logger.info(f"Dados detalhados da tabela carregados ({num_recibos} linhas)")
                    else:
                        logger.warning(f"Dia {dia} não encontrado em wizard_data, usando dados agregados")

                # Compatibilidade: Formato antigo {form: {...}, table: [...]} (sem separação por dia)
                elif isinstance(mapa.wizard_data, dict) and "form" in mapa.wizard_data:
                    logger.warning(f"Formato antigo detectado (sem separação por dia), convertendo...")
                    self._form_data = dict(mapa.wizard_data["form"])  # type: ignore

                    if "table" in mapa.wizard_data and mapa.wizard_data["table"]:
                        self._table_data = list(mapa.wizard_data["table"])  # type: ignore
                        table_data_loaded = True
                        num_recibos = len(self._table_data)
                        logger.info(f"Dados detalhados da tabela carregados ({num_recibos} linhas - formato antigo)")
                else:
                    # Formato muito antigo: apenas form data
                    self._form_data = dict(mapa.wizard_data)  # type: ignore
                    logger.info(f"Dados do formulário carregados (formato muito antigo) para {dia}/{mes}/{ano}")

            # 4. Se não temos dados detalhados, reconstruir a partir da linha agregada
            if not table_data_loaded:
                logger.info("Reconstruindo dados da tabela a partir de linha agregada...")
                table_data: list[dict[str, object]] = []

                # Verificar valores não-nulos
                recibo_inicio: int = linha.recibo_inicio or 0
                recibo_fim: int = linha.recibo_fim or 0
                valor_com_iva: Decimal = linha.valor_com_iva or Decimal(0)
                km: Decimal = linha.km or Decimal(0)
                ips: int = linha.ips or 0

                # Criar linhas de recibo baseado no range
                num_recibos = recibo_fim - recibo_inicio + 1

                # CRÍTICO: Reconstruir campos do formulário a partir dos dados da linha
                self._form_data["quantidade_recibos"] = str(num_recibos)
                self._form_data["recibo_inicio"] = str(recibo_inicio)
                self._form_data["recibo_fim"] = str(recibo_fim)
                self._form_data["total_km"] = f"{float(km):.1f}".replace(".", ",")
                logger.info(f"Campos do formulário reconstruídos: Qtd={num_recibos}, Inicio={recibo_inicio}, Fim={recibo_fim}")

                # Dividir valores totais igualmente entre recibos (simplificação)
                valor_por_recibo: float = float(valor_com_iva) / num_recibos if num_recibos > 0 else 0.0
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

            # LOG DETALHADO: Dados ENVIADOS para o FRONTEND
            logger.info("=" * 100)
            logger.info("📤 DADOS ENVIADOS PARA O FRONTEND:")
            logger.info("=" * 100)
            logger.info(f"   Data carregada: {date.toString('dd/MM/yyyy')}")
            logger.info(f"   _form_data: {self._form_data}")
            logger.info(f"   _table_data ({len(self._table_data)} linhas):")
            for i, row in enumerate(self._table_data, 1):
                logger.info(f"      Linha {i}: {row}")
            logger.info(f"   Método de carregamento: {'DADOS DETALHADOS (wizard_data)' if table_data_loaded else 'RECONSTRUÍDO (linha agregada)'}")
            logger.info("=" * 100)

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
