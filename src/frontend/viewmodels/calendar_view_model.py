"""ViewModel para gerenciar estados do calendário.

Responsabilidades:
- Rastrear dias salvos (verde)
- Rastrear dias modificados (amarelo)
- Carregar estados do mês da BD
- Fornecer cores para células do calendário
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QColor

from src.db.models.mapas import TabelaTaxas
from src.frontend.viewmodels.base_view_model import BaseViewModel

if TYPE_CHECKING:
    from src.repositories.tabela_taxas_repository import TabelaTaxasRepository

logger: logging.Logger = logging.getLogger(__name__)


class DayState:
    """Estados possíveis de um dia no calendário."""

    SAVED = "saved"  # Verde: dia salvo na BD
    MODIFIED = "modified"  # Amarelo: dia modificado mas não salvo
    EMPTY = "empty"  # Sem cor: sem dados


class CalendarViewModel(BaseViewModel):
    """ViewModel para gerenciar estados do calendário.

    Gerencia cores e estados dos dias no calendário baseado em
    dados salvos na BD e modificações locais.
    """

    # Signals
    day_states_updated = Signal()  # Quando estados dos dias mudam

    def __init__(self, repository: TabelaTaxasRepository) -> None:
        """Inicializa o CalendarViewModel.

        Args:
            repository: Repository para acessar dados de assiduidade
        """
        super().__init__()
        self._repository: TabelaTaxasRepository = repository

        # Conjuntos de dias por estado
        # Formato: {(year, month, day)}
        self._saved_days: set[tuple[int, int, int]] = set()
        self._modified_days: set[tuple[int, int, int]] = set()

        logger.debug("CalendarViewModel inicializado")

    def on_appear(self) -> None:
        """Chamado quando calendário aparece."""
        logger.info("CalendarViewModel apareceu")

    async def load_month_states(self, year: int, month: int) -> None:
        """Carrega estados dos dias de um mês da BD.

        Args:
            year: Ano
            month: Mês (1-12)
        """
        try:
            # Buscar mapa do mês
            mapa: TabelaTaxas | None = self._repository.buscar_por_mes_ano(
                month, year)

            if not mapa:
                logger.debug(f"Nenhum mapa encontrado para {month}/{year}")
                return

            # Marcar dias que têm linhas salvas
            for linha in mapa.linhas:
                key: tuple[int, int, int] = (year, month, linha.dia)
                self._saved_days.add(key)
                logger.debug(
                    f"Dia {linha.dia}/{month}/{year} marcado como salvo")

            # Emitir signal para atualizar UI
            self.day_states_updated.emit()

            logger.info(
                f"Estados do mês {month}/{year} \
                    carregados: {len(mapa.linhas)} dias")

        except Exception as e:
            logger.error(
                f"Erro ao carregar estados do mês {month}/{year}: {e}",
                exc_info=True)

    def mark_day_modified(self, date: QDate) -> None:
        """Marca dia como modificado (amarelo).

        Args:
            date: Data a marcar como modificada
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())

        # Adicionar a modificados
        self._modified_days.add(key)

        # Remover de salvos se estava lá
        self._saved_days.discard(key)

        # Emitir signal
        self.day_states_updated.emit()

        logger.debug(
            f"Dia {date.toString('dd/MM/yyyy')} marcado como modificado")

    def mark_day_saved(self, date: QDate) -> None:
        """Marca dia como salvo (verde).

        Args:
            date: Data a marcar como salva
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())

        # Adicionar a salvos
        self._saved_days.add(key)

        # Remover de modificados
        self._modified_days.discard(key)

        # Emitir signal
        self.day_states_updated.emit()

        logger.info(f"Dia {date.toString('dd/MM/yyyy')} marcado como salvo")

    def mark_day_deleted(self, date: QDate) -> None:
        """Marca dia como eliminado (remove de salvos e modificados).

        Args:
            date: Data a marcar como eliminada
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())

        # Remover de ambos os conjuntos
        self._saved_days.discard(key)
        self._modified_days.discard(key)

        # Emitir signal
        self.day_states_updated.emit()

        logger.info(
            f"Dia {date.toString('dd/MM/yyyy')} \
                marcado como eliminado (removido do calendário)")

    def get_day_color(self, date: QDate) -> QColor | None:
        """Retorna cor baseada no estado do dia.

        Args:
            date: Data para verificar

        Returns:
            QColor para o estado ou None se sem estado especial
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())

        if key in self._saved_days:
            # Verde claro para dias salvos
            return QColor("#d4edda")
        elif key in self._modified_days:
            # Amarelo claro para dias modificados
            return QColor("#fff3cd")
        else:
            # Sem cor especial
            return None

    def is_day_saved(self, date: QDate) -> bool:
        """Verifica se dia está salvo.

        Args:
            date: Data a verificar

        Returns:
            True se dia está salvo
        """
        key: tuple[int, int, int] = (date.year(), date.month(), date.day())
        return key in self._saved_days

    def clear_month(self, year: int, month: int) -> None:
        """Limpa estados de um mês.

        Args:
            year: Ano
            month: Mês (1-12)
        """
        # Remover dias do mês
        self._saved_days = {
            (y, m, d) for (y, m, d) in self._saved_days
            if not (y == year and m == month)
        }
        self._modified_days = {
            (y, m, d) for (y, m, d) in self._modified_days
            if not (y == year and m == month)
        }

        # Emitir signal
        self.day_states_updated.emit()

        logger.debug(f"Estados do mês {month}/{year} limpos")

    def dispose(self) -> None:
        """Limpa recursos do ViewModel."""
        self._saved_days.clear()
        self._modified_days.clear()
        logger.info("CalendarViewModel descartado")
