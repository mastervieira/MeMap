"""Testes de integração para o sistema MeMap.

Testa fluxos completos que envolvem múltiplos componentes:
- Criação e manipulação de mapas
- Integração entre repositórios e modelos
- Fluxos de trabalho do usuário
"""

import pytest
from datetime import datetime, timezone
from decimal import Decimal

from src.db.models.base_mixin import EstadoDocumento, TipoDiaAssiduidade
from src.db.models.mapas import MapaAssiduidade, MapaTaxas
from src.repositories.assiduidade_repository import MapaAssiduidadeRepository
from src.repositories.taxas_repositorie import MapaTaxasRepository


class TestMapaAssiduidadeFluxoCompleto:
    """Testes de integração para fluxo completo de Mapa de Assiduidade."""

    def test_fluxo_completo_assiduidade(self, session, mapa_assiduidade_repo):
        """Testa fluxo completo: criação → adição de dias → cálculo de totais → finalização."""
        # 1. Criação do mapa
        mapa_data = {
            "mes": 1,
            "ano": 2024,
            "estado": EstadoDocumento.RASCUNHO,
            "wizard_data": {"stage": 1, "data": "test"},
        }
        mapa = mapa_assiduidade_repo.criar(**mapa_data)

        assert mapa.id is not None
        assert mapa.estado == EstadoDocumento.RASCUNHO
        assert mapa.total_dias_trabalho == 0

        # 2. Adição de dias
        dias_data = [
            {
                "dia": 1,
                "dia_semana": "Segunda-feira",
                "tipo": "trabalho",
                "ips": 8,
                "valor_sem_iva": "50.0",
                "km": "50.0",
            },
            {
                "dia": 2,
                "dia_semana": "Terça-feira",
                "tipo": "ausencia",
                "motivo": "Doença",
            },
            {
                "dia": 3,
                "dia_semana": "Quarta-feira",
                "tipo": "ferias",
            },
            {
                "dia": 4,
                "dia_semana": "Quinta-feira",
                "tipo": "trabalho",
                "ips": 8,
                "valor_sem_iva": "60.0",
                "km": "70.0",
            },
        ]

        linhas = mapa_assiduidade_repo.adicionar_dias_bulk(mapa.id, dias_data)
        assert len(linhas) == 4

        # 3. Cálculo de totais
        mapa_atualizado = mapa_assiduidade_repo.recalcular_totais(mapa.id)

        assert mapa_atualizado.total_dias_trabalho == 2
        assert mapa_atualizado.total_km == Decimal("120.0")  # 50 + 70
        assert mapa_atualizado.total_ips == 16  # 8 + 8
        assert mapa_atualizado.total_faturacao == Decimal("110.0")  # 50 + 60
        assert mapa_atualizado.total_ausencias == 1
        assert mapa_atualizado.total_ferias == 1
        assert mapa_atualizado.total_feriados == 0

        # 4. Finalização do mapa
        mapa_finalizado = mapa_assiduidade_repo.finalizar(mapa.id)
        assert mapa_finalizado.estado == EstadoDocumento.FECHADO
        assert mapa_finalizado.finalizado_em is not None

        # 5. Verificação final
        mapa_verificado = mapa_assiduidade_repo.buscar_por_id(mapa.id)
        assert mapa_verificado.estado == EstadoDocumento.FECHADO
        assert len(mapa_verificado.linhas) == 4
        assert mapa_verificado.total_dias_trabalho == 2

    def test_busca_por_mes_ano_com_varias_versoes(self, session, mapa_assiduidade_repo):
        """Testa busca por mês/ano retornando a versão mais recente."""
        # Cria duas versões do mesmo mapa
        mapa_data = {
            "mes": 1,
            "ano": 2024,
            "estado": EstadoDocumento.RASCUNHO,
        }

        mapa_v1 = mapa_assiduidade_repo.criar(**mapa_data)
        mapa_assiduidade_repo.adicionar_dia(mapa_v1.id, 1, "Segunda-feira")

        mapa_v2 = mapa_assiduidade_repo.criar(**mapa_data)
        mapa_assiduidade_repo.adicionar_dia(mapa_v2.id, 1, "Segunda-feira")
        mapa_assiduidade_repo.adicionar_dia(mapa_v2.id, 2, "Terça-feira")

        # Busca deve retornar a versão mais recente (v2)
        mapa_encontrado = mapa_assiduidade_repo.buscar_por_mes_ano(1, 2024)
        assert mapa_encontrado.id == mapa_v2.id
        assert len(mapa_encontrado.linhas) == 2

    def test_reabertura_e_edicao(self, session, mapa_assiduidade_repo):
        """Testa reabertura de mapa fechado e edição subsequente."""
        # Cria e finaliza um mapa
        mapa = mapa_assiduidade_repo.criar(mes=1, ano=2024)
        mapa_assiduidade_repo.adicionar_dia(mapa.id, 1, "Segunda-feira", TipoDiaAssiduidade.TRABALHO)
        mapa_assiduidade_repo.finalizar(mapa.id)

        mapa_fechado = mapa_assiduidade_repo.buscar_por_id(mapa.id)
        assert mapa_fechado.estado == EstadoDocumento.FECHADO

        # Reabre o mapa
        mapa_reaberto = mapa_assiduidade_repo.reabrir(mapa.id, "Correção de dados")
        assert mapa_reaberto.estado == EstadoDocumento.RASCUNHO
        assert mapa_reaberto.reopen_count == 1

        # Adiciona novo dia
        mapa_assiduidade_repo.adicionar_dia(mapa.id, 2, "Terça-feira", TipoDiaAssiduidade.TRABALHO)
        mapa_assiduidade_repo.recalcular_totais(mapa.id)

        mapa_editado = mapa_assiduidade_repo.buscar_por_id(mapa.id)
        assert mapa_editado.total_dias_trabalho == 2
        assert mapa_editado.reopen_count == 1


class TestMapaTaxasFluxoCompleto:
    """Testes de integração para fluxo completo de Mapa de Taxas."""

    def test_fluxo_completo_taxas(self, session, mapa_taxas_repo):
        """Testa fluxo completo: criação → adição de linhas → cálculo de totais → finalização."""
        # 1. Criação do mapa
        mapa_data = {
            "mes": 1,
            "ano": 2024,
            "estado": EstadoDocumento.RASCUNHO,
            "wizard_data": {"stage": 2, "data": "test"},
        }
        mapa = mapa_taxas_repo.criar(**mapa_data)

        assert mapa.id is not None
        assert mapa.estado == EstadoDocumento.RASCUNHO
        assert mapa.total_setubal == Decimal("0")

        # 2. Adição de linhas
        linhas_data = [
            {
                "ordem": 1,
                "recibo": 100,
                "setubal": "100.0",
                "santarem": "50.0",
                "evora": "25.0",
                "ips": 8,
                "dividas": "10.0",
            },
            {
                "ordem": 2,
                "recibo": 101,
                "setubal": "200.0",
                "santarem": "100.0",
                "evora": "50.0",
                "ips": 16,
                "dividas": "20.0",
            },
        ]

        linhas = mapa_taxas_repo.adicionar_linhas_bulk(mapa.id, linhas_data)
        assert len(linhas) == 2

        # 3. Cálculo de totais
        mapa_atualizado = mapa_taxas_repo.calcular_totais(mapa.id)

        assert mapa_atualizado.total_setubal == Decimal("300.0")
        assert mapa_atualizado.total_santarem == Decimal("150.0")
        assert mapa_atualizado.total_evora == Decimal("75.0")
        assert mapa_atualizado.total_ips == 24
        assert mapa_atualizado.total_dividas == Decimal("30.0")
        assert mapa_atualizado.total_faturacao == Decimal("525.0")

        # 4. Finalização do mapa
        mapa_finalizado = mapa_taxas_repo.finalizar(mapa.id)
        assert mapa_finalizado.estado == EstadoDocumento.FECHADO
        assert mapa_finalizado.finalizado_em is not None

        # 5. Verificação final
        mapa_verificado = mapa_taxas_repo.buscar_por_id(mapa.id)
        assert mapa_verificado.estado == EstadoDocumento.FECHADO
        assert len(mapa_verificado.linhas) == 2
        assert mapa_verificado.total_setubal == Decimal("300.0")

    def test_atualizacao_pdf_path(self, session, mapa_taxas_repo):
        """Testa atualização do caminho do PDF e persistência."""
        mapa = mapa_taxas_repo.criar(mes=1, ano=2024)
        pdf_path = "/data/pdfs/mapa_taxas_2024_01.pdf"

        mapa_atualizado = mapa_taxas_repo.atualizar_pdf_path(mapa.id, pdf_path)
        assert mapa_atualizado.pdf_path == pdf_path

        # Verifica persistência
        mapa_verificado = mapa_taxas_repo.buscar_por_id(mapa.id)
        assert mapa_verificado.pdf_path == pdf_path


class TestIntegracaoEntreRepositorios:
    """Testes de integração entre diferentes repositórios."""

    def test_criacao_conjunta_de_mapas(self, session, mapa_assiduidade_repo, mapa_taxas_repo):
        """Testa criação de mapas de assiduidade e taxas para o mesmo período."""
        mes, ano = 1, 2024

        # Cria mapa de assiduidade
        mapa_assiduidade = mapa_assiduidade_repo.criar(mes=mes, ano=ano)
        mapa_assiduidade_repo.adicionar_dia(mapa_assiduidade.id, 1, "Segunda-feira")

        # Cria mapa de taxas
        mapa_taxas = mapa_taxas_repo.criar(mes=mes, ano=ano)
        mapa_taxas_repo.adicionar_linha(mapa_taxas.id, 1, 100, Decimal("100.0"))

        # Verifica ambos os mapas
        assert mapa_assiduidade.mes == mes
        assert mapa_assiduidade.ano == ano
        assert mapa_taxas.mes == mes
        assert mapa_taxas.ano == ano

        # Busca por mês/ano deve retornar ambos
        mapa_assiduidade_encontrado = mapa_assiduidade_repo.buscar_por_mes_ano(mes, ano)
        mapa_taxas_encontrado = mapa_taxas_repo.buscar_por_mes_ano(mes, ano)

        assert mapa_assiduidade_encontrado.id == mapa_assiduidade.id
        assert mapa_taxas_encontrado.id == mapa_taxas.id

    def test_listagem_ordenada_de_mapas(self, session, mapa_assiduidade_repo, mapa_taxas_repo):
        """Testa listagem ordenada de mapas por data."""
        # Cria mapas em ordem cronológica
        datas = [(1, 2024), (2, 2024), (12, 2023)]

        for mes, ano in datas:
            mapa_assiduidade_repo.criar(mes=mes, ano=ano)
            mapa_taxas_repo.criar(mes=mes, ano=ano)

        # Listagem deve ser ordenada por ano/mês descendente
        mapas_assiduidade = mapa_assiduidade_repo.listar_todos()
        mapas_taxas = mapa_taxas_repo.listar_todos()

        assert len(mapas_assiduidade) == 3
        assert len(mapas_taxas) == 3

        # Verifica ordem: (2, 2024), (1, 2024), (12, 2023)
        assert mapas_assiduidade[0].mes == 2
        assert mapas_assiduidade[0].ano == 2024
        assert mapas_assiduidade[1].mes == 1
        assert mapas_assiduidade[1].ano == 2024
        assert mapas_assiduidade[2].mes == 12
        assert mapas_assiduidade[2].ano == 2023


class TestErrosEExcecoes:
    """Testes para tratamento de erros e exceções."""

    def test_criacao_mapa_com_dados_invalidos(self, mapa_assiduidade_repo):
        """Testa criação de mapa com dados inválidos."""
        with pytest.raises(ValueError, match="Mês inválido"):
            mapa_assiduidade_repo.criar(mes=13, ano=2024)

        with pytest.raises(ValueError, match="Ano inválido"):
            mapa_assiduidade_repo.criar(mes=1, ano=1999)

    def test_operacoes_em_mapa_inexistente(self, mapa_assiduidade_repo):
        """Testa operações em mapa inexistente."""
        with pytest.raises(ValueError):
            mapa_assiduidade_repo.buscar_por_id(999)

        with pytest.raises(ValueError):
            mapa_assiduidade_repo.finalizar(999)

        with pytest.raises(ValueError):
            mapa_assiduidade_repo.recalcular_totais(999)

    def test_adicao_de_dias_em_mapa_inexistente(self, mapa_assiduidade_repo):
        """Testa adição de dias em mapa inexistente."""
        with pytest.raises(Exception):  # Deve gerar erro de integridade referencial
            mapa_assiduidade_repo.adicionar_dia(999, 1, "Segunda-feira")

    def test_finalizacao_de_mapa_ja_fechado(self, mapa_assiduidade_repo):
        """Testa finalização de mapa já fechado."""
        mapa = mapa_assiduidade_repo.criar(mes=1, ano=2024)
        mapa_assiduidade_repo.finalizar(mapa.id)

        with pytest.raises(ValueError, match="já fechado"):
            mapa_assiduidade_repo.finalizar(mapa.id)
