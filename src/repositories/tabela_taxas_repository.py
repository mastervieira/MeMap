"""Repository para Tabela de Taxas.

Implementa padrão Repository para TabelaTaxas e TabelaTaxasLinha.
Tabela base com dados primários (valores COM IVA) inseridos pelo utilizador.

A partir desta tabela serão gerados posteriormente os mapas derivados:
- Mapa de Assiduidade (com conversão para valores sem IVA)
- Mapa de Taxas
- Outros mapas

Transições de estado são delegadas ao EstadoManager centralizado.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session, joinedload

from src.common.constants.enums import EstadoDocumento, TipoDiaAssiduidade
from src.common.execptions.assiduidade import (
    TabelaTaxasInvalidStateError,
    TabelaTaxasNotFoundError,
    TabelaTaxasPersistenceError,
    TabelaTaxasValidationError,
)
from src.db.models.mapas import TabelaTaxas, TabelaTaxasLinha

logger = logging.getLogger(__name__)


class TabelaTaxasRepository:
    """Repository para operações de persistência da Tabela de Taxas.

    Tabela base que armazena dados primários com valores COM IVA.

    Responsável por:
    - CRUD para TabelaTaxas (cabeçalho mês/ano)
    - Gestão de TabelaTaxasLinha (dados diários)
    - Transformação wizard_data → linhas de dados
    - Base para geração posterior de mapas derivados
    """

    def __init__(self, session: Session) -> None:
        """Inicializa o repository.

        Args:
            session: Sessão do SQLAlchemy
        """
        self._session = session

    @property
    def session(self) -> Session:
        """Acesso à sessão (compatibilidade)."""
        return self._session

    # =========================================================================
    # IRepository INTERFACE METHODS
    # =========================================================================

    def criar(
        self,
        mes: int | None = None,
        ano: int | None = None,
        estado: EstadoDocumento = EstadoDocumento.RASCUNHO,
        wizard_data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> TabelaTaxas:
        """Cria novo Mapa de Assiduidade.

        Args:
            mes: Mês (1-12)
            ano: Ano
            estado: Estado inicial
            wizard_data: Dados do wizard (JSON)
            **kwargs: Argumentos adicionais (ignorados)

        Returns:
            TabelaTaxas criado com ID

        Raises:
            ValueError: Se mes ou ano inválidos
        """
        # Validação de entrada
        if mes is None or ano is None:
            raise ValueError("Mes e ano são obrigatórios")
        if ano < 2000 or ano > 2100:
            raise ValueError(f"Ano inválido: {ano}. Deve ser entre 2000 e 2100")

        if not (1 <= mes <= 12):
            raise ValueError(f"Mês inválido: {mes}. Deve ser entre 1 e 12")

        try:
            mapa = TabelaTaxas(
                mes=mes,
                ano=ano,
                estado=estado,
                versao=1,
                wizard_data=wizard_data,
            )
            self._session.add(mapa)
            self._session.flush()
            self._session.commit()
            return mapa
        except Exception as e:
            # Não expõe o erro original para o cliente
            self._session.rollback()
            raise TabelaTaxasPersistenceError(
                operation="criar", original_error=e
            )

    def buscar_por_id(self, id: int) -> TabelaTaxas | None:
        """Busca Mapa de Assiduidade por ID.

        Args:
            id: ID do mapa

        Returns:
            TabelaTaxas ou None
        """
        try:
            return (
                self._session.query(TabelaTaxas)
                .options(joinedload(TabelaTaxas.linhas))
                .filter(TabelaTaxas.id == id)
                .first()
            )
        except Exception:
            return None

    def buscar_por_mes_ano(self, mes: int, ano: int) -> TabelaTaxas | None:
        """Busca Mapa de Assiduidade por mês/ano.

        Args:
            mes: Mês (1-12)
            ano: Ano

        Returns:
            TabelaTaxas ou None (mais recente se houver múltiplos)

        Raises:
            TabelaTaxasValidationError: Se mês ou ano inválidos
        """
        if not (1 <= mes <= 12):
            raise TabelaTaxasValidationError(
                field="mes",
                value=mes,
                reason=f"Mês inválido: {mes}. Deve ser entre 1 e 12"
            )
        if ano < 2000 or ano > 2100:
            raise TabelaTaxasValidationError(
                field="ano",
                value=ano,
                reason=f"Ano inválido: {ano}. Deve ser entre 2000 e 2100"
            )

        try:
            return (
                self._session.query(TabelaTaxas)
                .options(joinedload(TabelaTaxas.linhas))
                .filter(
                    TabelaTaxas.mes == mes,
                    TabelaTaxas.ano == ano,
                )
                .order_by(TabelaTaxas.versao.desc())
                .first()
            )
        except Exception as e:
            raise TabelaTaxasPersistenceError(
                operation="buscar por mes/ano", original_error=e
            )

    def buscar_todos(self) -> list[TabelaTaxas]:
        """Busca todos os Mapas de Assiduidade.

        Returns:
            Lista com todos os TabelaTaxas (com linhas carregadas)

        Raises:
            TabelaTaxasPersistenceError: Se erro ao buscar
        """
        try:
            return (
                self._session.query(TabelaTaxas)
                .options(joinedload(TabelaTaxas.linhas))
                .order_by(TabelaTaxas.ano.desc(), TabelaTaxas.mes.desc())
                .all()
            )
        except Exception as e:
            raise TabelaTaxasPersistenceError(
                operation="buscar todos", original_error=e
            )

    def atualizar(self, entity: TabelaTaxas) -> None:
        """Atualiza Mapa de Assiduidade.

        Args:
            entity: Entidade a atualizar

        Raises:
            ValueError: Se entidade inválida
        """
        if entity is None:
            raise ValueError("Entidade não pode ser None")
        try:
            entity.updated_at = datetime.now()
            self._session.flush()
        except Exception as e:
            raise RuntimeError(
                f"Erro ao atualizar TabelaTaxas: {e}"
            ) from e

    def eliminar(self, id: int) -> bool:
        """Elimina Mapa de Assiduidade por ID.

        Args:
            id: ID do mapa

        Returns:
            True se eliminou, False se não encontrou
        """
        try:
            mapa = (
                self._session.query(TabelaTaxas)
                .filter(TabelaTaxas.id == id)
                .first()
            )
            if not mapa:
                return False
            self._session.delete(mapa)
            self._session.flush()
            return True
        except Exception:
            return False

    def listar_todos(self) -> list[TabelaTaxas]:
        """Lista todos os Mapas de Assiduidade.

        Returns:
            Lista de TabelaTaxas ordenada por ano/mês descendente
        """
        try:
            return (
                self._session.query(TabelaTaxas)
                .order_by(
                    TabelaTaxas.ano.desc(), TabelaTaxas.mes.desc()
                )
                .all()
            )
        except Exception:
            return []

    # =========================================================================
    # MÉTODOS ADICIONAIS (compatibilidade)
    # =========================================================================

    def listar_por_ano(self, ano: int | None = None) -> list[TabelaTaxas]:
        """Lista mapas por ano.

        Args:
            ano: Filtrar por ano (opcional)

        Returns:
            Lista de TabelaTaxas
        """
        try:
            query = self._session.query(TabelaTaxas)
            if ano:
                query = query.filter(TabelaTaxas.ano == ano)
            return query.order_by(
                TabelaTaxas.ano.desc(), TabelaTaxas.mes.desc()
            ).all()
        except Exception:
            return []

    def deletar(self, mapa_id: int) -> bool:
        """Deleta Mapa de Assiduidade (alias para eliminar - compatibilidade).

        Args:
            mapa_id: ID do mapa

        Returns:
            True se deletou, False se não encontrou
        """
        return self.eliminar(mapa_id)

    # =========================================================================
    # GESTÃO DE LINHAS (DIAS)
    # =========================================================================

    def adicionar_dia(
        self,
        mapa_id: int,
        dia: int,
        dia_semana: str,
        tipo: TipoDiaAssiduidade = TipoDiaAssiduidade.TRABALHO,
        recibo_inicio: int | None = None,
        recibo_fim: int | None = None,
        ips: int = 0,
        valor_com_iva: Decimal = Decimal("0"),
        locais: str | None = None,
        km: Decimal = Decimal("0"),
        motivo: str | None = None,
        periodo: str | None = None,
        observacoes: str | None = None,
    ) -> TabelaTaxasLinha:
        """Adiciona dia ao mapa.

        Args:
            mapa_id: ID do mapa
            dia: Dia do mês (1-31)
            dia_semana: Nome do dia (Segunda, Terça, etc.)
            tipo: Tipo de dia
            recibo_inicio/fim: Recibos do dia
            ips: IPS do dia
            valor_com_iva: Valor facturado
            locais: Locais visitados
            km: KMs percorridos
            motivo: Motivo (para ausência)
            periodo: Manhã/Tarde/Dia completo
            observacoes: Notas adicionais

        Returns:
            TabelaTaxasLinha criada
        """
        linha = TabelaTaxasLinha(
            mapa_id=mapa_id,
            dia=dia,
            dia_semana=dia_semana,
            tipo=tipo,
            recibo_inicio=recibo_inicio,
            recibo_fim=recibo_fim,
            ips=ips,
            valor_com_iva=valor_com_iva,
            locais=locais,
            km=km,
            motivo=motivo,
            periodo=periodo,
            observacoes=observacoes,
        )
        self._session.add(linha)
        self._session.flush()
        return linha

    def adicionar_dias_bulk(
        self, mapa_id: int, dias_data: list[dict[str, int | str | Decimal | None]]
    ) -> list[TabelaTaxasLinha]:
        """Adiciona múltiplos dias de uma vez.

        Args:
            mapa_id: ID do mapa
            dias_data: Lista de dicts com dados dos dias

        Returns:
            Lista de TabelaTaxasLinha criadas
        """
        dias = []
        for data in dias_data:
            # Converter tipo string para enum
            tipo = data.get("tipo", "trabalho")
            if isinstance(tipo, str):
                tipo = TipoDiaAssiduidade(tipo)

            linha = TabelaTaxasLinha(
                mapa_id=mapa_id,
                dia=data["dia"],
                dia_semana=data.get("dia_semana", ""),
                tipo=tipo,
                recibo_inicio=data.get("recibo_inicio"),
                recibo_fim=data.get("recibo_fim"),
                ips=data.get("ips", 0),
                valor_com_iva=Decimal(str(data.get("valor_com_iva", 0))),
                locais=data.get("locais"),
                km=Decimal(str(data.get("km", 0))),
                motivo=data.get("motivo"),
                periodo=data.get("periodo"),
                observacoes=data.get("observacoes"),
            )
            dias.append(linha)
            self._session.add(linha)
        self._session.flush()
        return dias  # type: ignore

    def limpar_dias(self, mapa_id: int) -> int:
        """Remove todos os dias de um mapa.

        Args:
            mapa_id: ID do mapa

        Returns:
            Número de dias removidos
        """
        count = (
            self._session.query(TabelaTaxasLinha)
            .filter(TabelaTaxasLinha.mapa_id == mapa_id)
            .delete()
        )
        self._session.flush()
        return count

    # =========================================================================
    # GESTÃO DE ESTADOS
    # =========================================================================

    def finalizar(self, mapa_id: int) -> TabelaTaxas:
        """Muda estado para FECHADO (finalizado).

        Args:
            mapa_id: ID do mapa

        Returns:
            TabelaTaxas atualizado

        Raises:
            TabelaTaxasNotFoundError: Se mapa não encontrado
            TabelaTaxasInvalidStateError: Se mapa já fechado
        """
        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise TabelaTaxasNotFoundError(mapa_id)

        # Permitir finalizar se RASCUNHO ou ABERTO (reaberto para edição)
        estados_editaveis = [EstadoDocumento.RASCUNHO, EstadoDocumento.ABERTO]
        if mapa.estado not in estados_editaveis:
            raise TabelaTaxasInvalidStateError(
                mapa_id=mapa_id,
                current_state=mapa.estado,
                operation="finalizar"
            )

        mapa.estado = EstadoDocumento.FECHADO
        mapa.finalizado_em = datetime.now(timezone.utc)
        mapa.fechado_em = datetime.now(timezone.utc)
        mapa.updated_at = datetime.now(timezone.utc)
        self._session.flush()
        return mapa

    def fechar(self, mapa_id: int) -> TabelaTaxas:
        """Muda estado para FECHADO.

        Delega a transição para o EstadoManager centralizado.

        Args:
            mapa_id: ID do mapa

        Returns:
            TabelaTaxas atualizado

        Raises:
            TabelaTaxasNotFoundError: Se mapa não encontrado
            TabelaTaxasPersistenceError: Se erro de persistência
        """
        # TODO: Implementar EstadoManager quando estiver disponível
        # from mapa_contas.services.estado_manager import EstadoManager

        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise TabelaTaxasNotFoundError(mapa_id)

        # Simulação da lógica de fecho
        if mapa.estado != EstadoDocumento.ABERTO:
            raise TabelaTaxasInvalidStateError(
                mapa_id=mapa_id,
                current_state=mapa.estado,
                operation="fechar"
            )

        mapa.estado = EstadoDocumento.FECHADO
        mapa.updated_at = datetime.now(timezone.utc)
        self._session.flush()

        logger.info(f"TabelaTaxas id={mapa_id} fechado com sucesso")
        return mapa

    def reabrir(self, mapa_id: int, motivo: str) -> TabelaTaxas:
        """Reabre mapa FECHADO para RASCUNHO (permite edição completa).

        Delega a transição para o EstadoManager centralizado.

        Args:
            mapa_id: ID do mapa
            motivo: Motivo da reabertura (obrigatório)

        Returns:
            TabelaTaxas atualizado

        Raises:
            TabelaTaxasNotFoundError: Se mapa não encontrado
            TabelaTaxasPersistenceError: Se erro de persistência
        """
        # TODO: Implementar EstadoManager quando estiver disponível
        # from mapa_contas.services.estado_manager import EstadoManager

        try:
            mapa = (
                self._session.query(TabelaTaxas)
                .options(joinedload(TabelaTaxas.linhas))
                .filter(TabelaTaxas.id == mapa_id)
                .first()
            )

            if not mapa:
                raise TabelaTaxasNotFoundError(mapa_id)

            # Simples transição para RASCUNHO
            if mapa.estado != EstadoDocumento.FECHADO:
                raise TabelaTaxasInvalidStateError(
                    mapa_id=mapa_id,
                    current_state=mapa.estado,
                    operation="reabrir"
                )

            mapa.estado = EstadoDocumento.RASCUNHO
            mapa.reopen_count = (mapa.reopen_count or 0) + 1
            mapa.updated_at = datetime.now(timezone.utc)
            self._session.flush()
            self._session.commit()

            logger.info(
                f"TabelaTaxas id={mapa_id} reaberto com sucesso (motivo: {motivo})"
            )
            return mapa

        except TabelaTaxasNotFoundError:
            raise  # Re-lança a exceção específica
        except TabelaTaxasInvalidStateError:
            raise  # Re-lança a exceção específica
        except Exception as e:
            raise TabelaTaxasPersistenceError(
                operation="reabrir mapa", original_error=e
            )

    # =========================================================================
    # CÁLCULOS E TOTAIS
    # =========================================================================

    def recalcular_totais(self, mapa_id: int) -> TabelaTaxas:
        """Recalcula totais a partir dos dias.

        Args:
            mapa_id: ID do mapa

        Returns:
            TabelaTaxas com totais actualizados
        """
        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"TabelaTaxas id={mapa_id} não encontrado")

        # Contar dias por tipo e somar valores
        total_dias_trabalho = 0
        total_km = Decimal("0")
        total_ips = 0
        total_faturacao = Decimal("0")
        total_ausencias = 0
        total_ferias = 0
        total_feriados = 0

        for linha in mapa.linhas:
            if linha.tipo == TipoDiaAssiduidade.TRABALHO:
                total_dias_trabalho += 1
                total_km += linha.km or Decimal("0")
                total_ips += linha.ips or 0
                total_faturacao += linha.valor_com_iva or Decimal("0")
            elif linha.tipo == TipoDiaAssiduidade.AUSENCIA:
                total_ausencias += 1
            elif linha.tipo == TipoDiaAssiduidade.FERIAS:
                total_ferias += 1
            elif linha.tipo == TipoDiaAssiduidade.FERIADO:
                total_feriados += 1
            # SABADO e DOMINGO não contam

        mapa.total_dias_trabalho = total_dias_trabalho
        mapa.total_km = total_km
        mapa.total_ips = total_ips
        mapa.total_faturacao = total_faturacao
        mapa.total_ausencias = total_ausencias
        mapa.total_ferias = total_ferias
        mapa.total_feriados = total_feriados
        mapa.updated_at = datetime.now()

        self._session.flush()
        return mapa

    def atualizar_pdf_path(
        self, mapa_id: int, pdf_path: str
    ) -> TabelaTaxas:
        """Atualiza path do PDF gerado.

        Args:
            mapa_id: ID do mapa
            pdf_path: Caminho do PDF

        Returns:
            TabelaTaxas actualizado
        """
        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"TabelaTaxas id={mapa_id} não encontrado")

        mapa.pdf_path = pdf_path
        mapa.updated_at = datetime.now()
        self._session.flush()
        return mapa
