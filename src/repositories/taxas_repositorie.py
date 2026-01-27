"""Repository para Mapa de Assiduidade.

Implementa padrão Repository para MapaAssiduidade e MapaAssiduidadeLinha.
Implementa IRepository[MapaAssiduidade] para conformidade com contratos.

Transições de estado são delegadas ao EstadoManager centralizado.
"""

from __future__ import annotations

import logging
from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from sqlalchemy.orm import Session, joinedload

from db.models.base_mixin import EstadoDocumento, TipoDiaAssiduidade
from db.models.mapas import MapaAssiduidade, MapaAssiduidadeLinha

logger = logging.getLogger(__name__)


class MapaAssiduidadeRepository:
    """Repository para operações de persistência do Mapa de Assiduidade.

    Implementa IRepository[MapaAssiduidade] para conformidade com contratos.

    Responsável por:
    - CRUD para MapaAssiduidade (header)
    - Gestão de MapaAssiduidadeLinha (dias)
    - Transformação wizard_data → dias
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
    ) -> MapaAssiduidade:
        """Cria novo Mapa de Assiduidade.

        Args:
            mes: Mês (1-12)
            ano: Ano
            estado: Estado inicial
            wizard_data: Dados do wizard (JSON)
            **kwargs: Argumentos adicionais (ignorados)

        Returns:
            MapaAssiduidade criado com ID

        Raises:
            ValueError: Se mes ou ano inválidos
        """
        if mes is None or ano is None:
            raise ValueError("mes e ano são obrigatórios")
        if not (1 <= mes <= 12):
            raise ValueError(f"Mês inválido: {mes}")
        if ano < 2000 or ano > 2100:
            raise ValueError(f"Ano inválido: {ano}")

        try:
            mapa = MapaAssiduidade(
                mes=mes,
                ano=ano,
                estado=estado,
                versao=1,
                wizard_data=wizard_data,
                created_at=datetime.now(),
                updated_at=datetime.now(),
            )
            self._session.add(mapa)
            self._session.flush()
            return mapa
        except Exception as e:
            raise RuntimeError(f"Erro ao criar MapaAssiduidade: {e}") from e

    def buscar_por_id(self, id: int) -> MapaAssiduidade | None:
        """Busca Mapa de Assiduidade por ID.

        Args:
            id: ID do mapa

        Returns:
            MapaAssiduidade ou None
        """
        try:
            return (
                self._session.query(MapaAssiduidade)
                .options(joinedload(MapaAssiduidade.linhas))
                .filter(MapaAssiduidade.id == id)
                .first()
            )
        except Exception:
            return None

    def buscar_por_mes_ano(self, mes: int, ano: int) -> MapaAssiduidade | None:
        """Busca Mapa de Assiduidade por mês/ano.

        Args:
            mes: Mês (1-12)
            ano: Ano

        Returns:
            MapaAssiduidade ou None (mais recente se houver múltiplos)

        Raises:
            ValueError: Se mês ou ano inválidos
        """
        if not (1 <= mes <= 12):
            raise ValueError(f"Mês inválido: {mes}")
        if ano < 2000 or ano > 2100:
            raise ValueError(f"Ano inválido: {ano}")

        try:
            return (
                self._session.query(MapaAssiduidade)
                .options(joinedload(MapaAssiduidade.linhas))
                .filter(
                    MapaAssiduidade.mes == mes,
                    MapaAssiduidade.ano == ano,
                )
                .order_by(MapaAssiduidade.versao.desc())
                .first()
            )
        except Exception:
            return None

    def atualizar(self, entity: MapaAssiduidade) -> None:
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
                f"Erro ao atualizar MapaAssiduidade: {e}"
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
                self._session.query(MapaAssiduidade)
                .filter(MapaAssiduidade.id == id)
                .first()
            )
            if not mapa:
                return False
            self._session.delete(mapa)
            self._session.flush()
            return True
        except Exception:
            return False

    def listar_todos(self) -> list[MapaAssiduidade]:
        """Lista todos os Mapas de Assiduidade.

        Returns:
            Lista de MapaAssiduidade ordenada por ano/mês descendente
        """
        try:
            return (
                self._session.query(MapaAssiduidade)
                .order_by(
                    MapaAssiduidade.ano.desc(), MapaAssiduidade.mes.desc()
                )
                .all()
            )
        except Exception:
            return []

    # =========================================================================
    # MÉTODOS ADICIONAIS (compatibilidade)
    # =========================================================================

    def listar_por_ano(self, ano: int | None = None) -> list[MapaAssiduidade]:
        """Lista mapas por ano.

        Args:
            ano: Filtrar por ano (opcional)

        Returns:
            Lista de MapaAssiduidade
        """
        try:
            query = self._session.query(MapaAssiduidade)
            if ano:
                query = query.filter(MapaAssiduidade.ano == ano)
            return query.order_by(
                MapaAssiduidade.ano.desc(), MapaAssiduidade.mes.desc()
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
        recibo_inicio: Optional[int] = None,
        recibo_fim: Optional[int] = None,
        ips: int = 0,
        valor_sem_iva: Decimal = Decimal("0"),
        locais: Optional[str] = None,
        km: Decimal = Decimal("0"),
        motivo: Optional[str] = None,
        periodo: Optional[str] = None,
        observacoes: Optional[str] = None,
    ) -> MapaAssiduidadeLinha:
        """Adiciona dia ao mapa.

        Args:
            mapa_id: ID do mapa
            dia: Dia do mês (1-31)
            dia_semana: Nome do dia (Segunda, Terça, etc.)
            tipo: Tipo de dia
            recibo_inicio/fim: Recibos do dia
            ips: IPS do dia
            valor_sem_iva: Valor facturado
            locais: Locais visitados
            km: KMs percorridos
            motivo: Motivo (para ausência)
            periodo: Manhã/Tarde/Dia completo
            observacoes: Notas adicionais

        Returns:
            MapaAssiduidadeLinha criada
        """
        linha = MapaAssiduidadeLinha(
            mapa_id=mapa_id,
            dia=dia,
            dia_semana=dia_semana,
            tipo=tipo,
            recibo_inicio=recibo_inicio,
            recibo_fim=recibo_fim,
            ips=ips,
            valor_sem_iva=valor_sem_iva,
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
        self, mapa_id: int, dias_data: list[dict]
    ) -> list[MapaAssiduidadeLinha]:
        """Adiciona múltiplos dias de uma vez.

        Args:
            mapa_id: ID do mapa
            dias_data: Lista de dicts com dados dos dias

        Returns:
            Lista de MapaAssiduidadeLinha criadas
        """
        dias = []
        for data in dias_data:
            # Converter tipo string para enum
            tipo = data.get("tipo", "trabalho")
            if isinstance(tipo, str):
                tipo = TipoDiaAssiduidade(tipo)

            linha = MapaAssiduidadeLinha(
                mapa_id=mapa_id,
                dia=data["dia"],
                dia_semana=data.get("dia_semana", ""),
                tipo=tipo,
                recibo_inicio=data.get("recibo_inicio"),
                recibo_fim=data.get("recibo_fim"),
                ips=data.get("ips", 0),
                valor_sem_iva=Decimal(str(data.get("valor_sem_iva", 0))),
                locais=data.get("locais"),
                km=Decimal(str(data.get("km", 0))),
                motivo=data.get("motivo"),
                periodo=data.get("periodo"),
                observacoes=data.get("observacoes"),
            )
            dias.append(linha)
            self._session.add(linha)
        self._session.flush()
        return dias

    def limpar_dias(self, mapa_id: int) -> int:
        """Remove todos os dias de um mapa.

        Args:
            mapa_id: ID do mapa

        Returns:
            Número de dias removidos
        """
        count = (
            self._session.query(MapaAssiduidadeLinha)
            .filter(MapaAssiduidadeLinha.mapa_id == mapa_id)
            .delete()
        )
        self._session.flush()
        return count

    # =========================================================================
    # GESTÃO DE ESTADOS
    # =========================================================================

    def finalizar(self, mapa_id: int) -> MapaAssiduidade:
        """Muda estado para FECHADO (finalizado).

        Args:
            mapa_id: ID do mapa

        Returns:
            MapaAssiduidade atualizado

        Raises:
            ValueError: Se mapa não encontrado ou já fechado
        """
        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"MapaAssiduidade id={mapa_id} não encontrado")

        # Permitir finalizar se RASCUNHO ou ABERTO (reaberto para edição)
        estados_editaveis = [EstadoDocumento.RASCUNHO, EstadoDocumento.ABERTO]
        if mapa.estado not in estados_editaveis:
            raise ValueError(
                f"MapaAssiduidade id={mapa_id} está fechado e não pode ser alterado"
            )

        mapa.estado = EstadoDocumento.FECHADO
        mapa.finalizado_em = datetime.now()
        mapa.fechado_em = datetime.now()
        mapa.updated_at = datetime.now()
        self._session.flush()
        return mapa

    def fechar(self, mapa_id: int) -> MapaAssiduidade:
        """Muda estado para FECHADO.

        Delega a transição para o EstadoManager centralizado.

        Args:
            mapa_id: ID do mapa

        Returns:
            MapaAssiduidade atualizado

        Raises:
            ValueError: Se mapa não encontrado ou transição inválida
        """
        from mapa_contas.services.estado_manager import EstadoManager

        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"MapaAssiduidade id={mapa_id} não encontrado")

        manager = EstadoManager(self._session)
        resultado = manager.fechar(mapa)

        if not resultado.sucesso:
            logger.warning(
                f"Falha ao fechar MapaAssiduidade id={mapa_id}: {resultado.mensagem}"
            )
            raise ValueError(resultado.mensagem)

        logger.info(f"MapaAssiduidade id={mapa_id} fechado com sucesso")
        return mapa

    def reabrir(self, mapa_id: int, motivo: str) -> MapaAssiduidade:
        """Reabre mapa FECHADO para RASCUNHO (permite edição completa).

        Delega a transição para o EstadoManager centralizado.

        Args:
            mapa_id: ID do mapa
            motivo: Motivo da reabertura (obrigatório)

        Returns:
            MapaAssiduidade atualizado

        Raises:
            ValueError: Se mapa não encontrado, transição inválida ou motivo em falta
        """
        from mapa_contas.services.estado_manager import EstadoManager

        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"MapaAssiduidade id={mapa_id} não encontrado")

        manager = EstadoManager(self._session)
        resultado = manager.reabrir(mapa, motivo)

        if not resultado.sucesso:
            logger.warning(
                f"Falha ao reabrir MapaAssiduidade id={mapa_id}: {resultado.mensagem}"
            )
            raise ValueError(resultado.mensagem)

        logger.info(
            f"MapaAssiduidade id={mapa_id} reaberto com sucesso (motivo: {motivo})"
        )
        return mapa

    # =========================================================================
    # CÁLCULOS E TOTAIS
    # =========================================================================

    def recalcular_totais(self, mapa_id: int) -> MapaAssiduidade:
        """Recalcula totais a partir dos dias.

        Args:
            mapa_id: ID do mapa

        Returns:
            MapaAssiduidade com totais actualizados
        """
        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"MapaAssiduidade id={mapa_id} não encontrado")

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
                total_faturacao += linha.valor_sem_iva or Decimal("0")
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
    ) -> MapaAssiduidade:
        """Atualiza path do PDF gerado.

        Args:
            mapa_id: ID do mapa
            pdf_path: Caminho do PDF

        Returns:
            MapaAssiduidade actualizado
        """
        mapa = self.buscar_por_id(mapa_id)
        if not mapa:
            raise ValueError(f"MapaAssiduidade id={mapa_id} não encontrado")

        mapa.pdf_path = pdf_path
        mapa.updated_at = datetime.now()
        self._session.flush()
        return mapa
