"""DataService - Communication with repository and data management.

Handles all CRUD operations for wizard data.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm.attributes import flag_modified

from src.common.constants.enums import EstadoDocumento, TipoDiaAssiduidade
from src.db.models.mapas import TabelaTaxas

if TYPE_CHECKING:
    from src.frontend.wizard.models import FormData, TableRowData
    from src.repositories.tabela_taxas_repository import (
        TabelaTaxasRepository,
    )

logger: logging.Logger = logging.getLogger(__name__)


class DataService:
    """Manages data persistence and repository communication.

    Responsibilities:
    - Load/save mapa data from/to database
    - Create new mapas
    - Delete specific days
    - Update wizard data
    """

    def __init__(
        self, repository: TabelaTaxasRepository
    ) -> None:
        """Initialize DataService.

        Args:
            repository: TabelaTaxasRepository instance
        """
        self._repository = repository

    # ==================== HELPER METHODS (PRIVATE) ====================

    def _get_or_create_mapa(
        self, mes: int, ano: int
    ) -> TabelaTaxas:
        """Get existing mapa or create new one.

        Extracted from duplicated code in save/delete/load methods.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Returns:
            TabelaTaxas instance (existing or new)
        """
        # Try to load existing mapa
        mapa = self._repository.buscar_por_mes_ano(mes, ano)

        if mapa:
            logger.debug(
                f"Mapa encontrado: {mes}/{ano} (ID={mapa.id})"
            )
            return mapa

        # Create new mapa
        logger.info(
            f"Criando novo mapa para {mes}/{ano}"
        )
        mapa = self._repository.criar(
            mes=mes,
            ano=ano,
            estado=EstadoDocumento.RASCUNHO,
            wizard_data={"dias": {}},
        )
        logger.info(
            f"Mapa criado com ID={mapa.id}"
        )
        return mapa

    def _update_wizard_data(
        self,
        mapa: TabelaTaxas,
        dia: int,
        form_data: FormData,
        table_rows: list[TableRowData],
    ) -> None:
        """Update wizard_data for specific day.

        Extracted from duplicated code in save_current_day.
        CRITICAL: Uses flag_modified() for SQLAlchemy JSON tracking.

        Args:
            mapa: TabelaTaxas instance
            dia: Day (1-31)
            form_data: Form data from Stage 1
            table_rows: Table rows from Stage 2
        """
        # Initialize structure if needed
        if not isinstance(mapa.wizard_data, dict):
            mapa.wizard_data = {"dias": {}}

        # Type narrowing - after this point wizard_data is dict
        wizard_data: dict[str, object] = mapa.wizard_data

        if "dias" not in wizard_data:
            wizard_data["dias"] = {}

        # Type narrowing for dias
        dias = wizard_data["dias"]
        if not isinstance(dias, dict):
            wizard_data["dias"] = {}
            dias = wizard_data["dias"]

        # Update day data
        dia_str = str(dia)
        dias[dia_str] = {  # type: ignore[index]
            "form": form_data.to_dict(),
            "table": [row.to_dict() for row in table_rows],
        }

        # CRITICAL: Flag as modified for SQLAlchemy JSON tracking
        flag_modified(mapa, "wizard_data")

        logger.debug(
            f"wizard_data atualizado: dia {dia} com "
            f"{len(table_rows)} linhas"
        )

    def _format_locais(
        self, zona_primaria: str, zona_secundaria: str
    ) -> str:
        """Format work locations string.

        Args:
            zona_primaria: Primary zone (Setúbal/Santarém/Évora)
            zona_secundaria: Secondary zone

        Returns:
            Formatted string "Primary/Secondary" or just "Primary"
        """
        if zona_secundaria.strip():
            return f"{zona_primaria}/{zona_secundaria}"
        return zona_primaria

    # ==================== CRUD METHODS (PUBLIC) ====================

    def carregar_mapa(
        self, mes: int, ano: int
    ) -> TabelaTaxas | None:
        """Load mapa for specific month/year.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Returns:
            TabelaTaxas instance or None if not found

        Example:
            >>> svc = DataService(repo)
            >>> mapa = svc.carregar_mapa(2, 2026)
            >>> if mapa:
            ...     print(f"Mapa {mapa.mes}/{mapa.ano}")
        """
        mapa = self._repository.buscar_por_mes_ano(mes, ano)

        if mapa:
            logger.debug(
                f"Mapa carregado: {mes}/{ano} "
                f"(ID={mapa.id}, {len(mapa.linhas)} linhas)"
            )
        else:
            logger.debug(
                f"Mapa não encontrado: {mes}/{ano}"
            )

        return mapa

    def guardar_mapa(self, tabela: TabelaTaxas) -> None:
        """Save mapa to database.

        Recalculates totals, commits, and refreshes the instance.

        Args:
            tabela: TabelaTaxas instance to save

        Example:
            >>> svc = DataService(repo)
            >>> mapa = svc.criar_novo_mapa(2, 2026)
            >>> # ... modify mapa ...
            >>> svc.guardar_mapa(mapa)
        """
        logger.debug(
            f"Salvando mapa {tabela.mes}/{tabela.ano} "
            f"(ID={tabela.id})"
        )

        # Recalculate totals
        self._repository.recalcular_totais(tabela.id)

        # Commit changes
        self._repository.session.commit()

        # Refresh to get latest data from DB
        self._repository.session.refresh(tabela)

        logger.info(
            f"Mapa {tabela.mes}/{tabela.ano} salvo com sucesso"
        )

    def criar_novo_mapa(
        self, mes: int, ano: int
    ) -> TabelaTaxas:
        """Create new empty mapa.

        Args:
            mes: Month (1-12)
            ano: Year (e.g. 2026)

        Returns:
            New TabelaTaxas instance

        Example:
            >>> svc = DataService(repo)
            >>> mapa = svc.criar_novo_mapa(2, 2026)
            >>> print(mapa.mes, mapa.ano)
            2 2026
        """
        logger.info(
            f"Criando novo mapa para {mes}/{ano}"
        )

        mapa = self._repository.criar(
            mes=mes,
            ano=ano,
            estado=EstadoDocumento.RASCUNHO,
            wizard_data={"dias": {}},
        )

        logger.info(
            f"Mapa {mes}/{ano} criado com ID={mapa.id}"
        )

        return mapa

    def eliminar_dia(
        self, tabela: TabelaTaxas, dia: int
    ) -> None:
        """Delete specific day from mapa.

        Removes day from wizard_data and deletes corresponding line.
        If no lines remain, deletes entire mapa.
        Otherwise, recalculates totals.

        Args:
            tabela: TabelaTaxas instance
            dia: Day to delete (1-31)

        Example:
            >>> svc = DataService(repo)
            >>> mapa = svc.carregar_mapa(2, 2026)
            >>> svc.eliminar_dia(mapa, 15)  # Delete day 15
        """
        logger.info(
            f"Eliminando dia {dia} do mapa "
            f"{tabela.mes}/{tabela.ano}"
        )

        # Remove from wizard_data with type narrowing
        dia_str = str(dia)
        if isinstance(tabela.wizard_data, dict):
            wizard_data: dict[str, object] = tabela.wizard_data
            if "dias" in wizard_data:
                dias = wizard_data["dias"]
                if isinstance(dias, dict) and dia_str in dias:
                    del dias[dia_str]
                    flag_modified(tabela, "wizard_data")
                    logger.debug(
                        f"Dia {dia} removido de wizard_data"
                    )

        # Find and delete corresponding line
        linha_to_delete = None
        for linha in tabela.linhas:
            if linha.dia == dia:
                linha_to_delete = linha
                break

        if linha_to_delete:
            self._repository.session.delete(linha_to_delete)
            self._repository.session.flush()
            logger.debug(
                f"Linha do dia {dia} deletada "
                f"(ID={linha_to_delete.id})"
            )

        # Refresh to update linhas list
        self._repository.session.refresh(tabela)

        # Check if mapa still has lines
        if len(tabela.linhas) == 0:
            # No lines left - delete entire mapa
            logger.info(
                f"Mapa {tabela.mes}/{tabela.ano} "
                "não tem mais linhas. Eliminando mapa inteiro."
            )
            self._repository.session.delete(tabela)
            self._repository.session.commit()
            logger.info(
                f"Mapa {tabela.mes}/{tabela.ano} eliminado"
            )
        else:
            # Recalculate totals and save
            logger.debug(
                f"Mapa {tabela.mes}/{tabela.ano} "
                f"ainda tem {len(tabela.linhas)} linhas. "
                "Recalculando totais."
            )
            self._repository.recalcular_totais(tabela.id)
            self._repository.session.commit()
            self._repository.session.refresh(tabela)
            logger.info(
                f"Dia {dia} eliminado. "
                f"Mapa {tabela.mes}/{tabela.ano} atualizado."
            )

    def atualizar_wizard_data(
        self,
        tabela: TabelaTaxas,
        dia: int,
        form_data: FormData,
        table_rows: list[TableRowData],
    ) -> None:
        """Update wizard data in mapa for specific day.

        Public wrapper for _update_wizard_data with validation.

        Args:
            tabela: TabelaTaxas instance
            dia: Day (1-31)
            form_data: Form data from Stage 1
            table_rows: Table rows from Stage 2

        Example:
            >>> svc = DataService(repo)
            >>> mapa = svc.carregar_mapa(2, 2026)
            >>> form = FormData(...)
            >>> rows = [TableRowData(...), ...]
            >>> svc.atualizar_wizard_data(mapa, 15, form, rows)
        """
        if not 1 <= dia <= 31:
            raise ValueError(
                f"Dia inválido: {dia}. Deve estar entre 1 e 31"
            )

        self._update_wizard_data(
            tabela, dia, form_data, table_rows
        )

        logger.info(
            f"wizard_data atualizado para dia {dia} "
            f"no mapa {tabela.mes}/{tabela.ano}"
        )
