# type: ignore
"""Testes de integração para o sistema MeMap.

Testa fluxos completos que envolvem múltiplos componentes:
- Criação e manipulação de mapas
- Integração entre repositórios e modelos
- Fluxos de trabalho do usuário
"""

from decimal import Decimal

import pytest

from src.common.constants.enums import EstadoDocumento


class TestTabelaTaxasFluxoCompleto:
    """Testes de integração para fluxo completo de Tabela de Taxas."""

    def test_fluxo_completo_taxas(self, session, tabela_taxas_repo):
        """Testa fluxo completo: criação → adição de dias → cálculo de totais → finalização."""
        # 1. Criação da tabela
        tabela_data = {
            "mes": 1,
            "ano": 2024,
            "estado": EstadoDocumento.RASCUNHO,
            "wizard_data": {"stage": 1, "data": "test"},
        }
        tabela = tabela_taxas_repo.criar(**tabela_data)

        assert tabela.id is not None
        assert tabela.estado == EstadoDocumento.RASCUNHO
        assert tabela.total_dias_trabalho == 0

        # 2. Adição de dias
        dias_data = [
            {
                "dia": 1,
                "dia_semana": "Segunda-feira",
                "tipo": "trabalho",
                "ips": 8,
                "valor_com_iva": "50.0",
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
                "valor_com_iva": "60.0",
                "km": "70.0",
            },
        ]

        linhas = tabela_taxas_repo.adicionar_dias_bulk(tabela.id, dias_data)
        assert len(linhas) == 4

        # 3. Cálculo de totais
        tabela_atualizada = tabela_taxas_repo.recalcular_totais(tabela.id)

        assert tabela_atualizada.total_dias_trabalho == 2
        assert tabela_atualizada.total_km == Decimal("120.0")  # 50 + 70
        assert tabela_atualizada.total_ips == 16  # 8 + 8
        assert tabela_atualizada.total_faturacao == Decimal("110.0")  # 50 + 60
        assert tabela_atualizada.total_ausencias == 1
        assert tabela_atualizada.total_ferias == 1
        assert tabela_atualizada.total_feriados == 0

        # 4. Finalização da tabela
        tabela_finalizada = tabela_taxas_repo.finalizar(tabela.id)
        assert tabela_finalizada.estado == EstadoDocumento.FECHADO
        assert tabela_finalizada.finalizado_em is not None

        # 5. Verificação final
        tabela_verificada = tabela_taxas_repo.buscar_por_id(tabela.id)
        assert tabela_verificada.estado == EstadoDocumento.FECHADO
        assert len(tabela_verificada.linhas) == 4
        assert tabela_verificada.total_dias_trabalho == 2

    def test_busca_por_mes_ano_com_varias_versoes(self, session, tabela_taxas_repo):
        """Testa busca por mês/ano retornando a versão mais recente."""
        tabela_data = {
            "mes": 1,
            "ano": 2024,
            "estado": EstadoDocumento.RASCUNHO,
        }

        # Cria uma tabela
        tabela_v1 = tabela_taxas_repo.criar(**tabela_data)

        # Busca retorna a tabela criada
        tabela_encontrada = tabela_taxas_repo.buscar_por_mes_ano(1, 2024)
        assert tabela_encontrada.id == tabela_v1.id

    def test_reabertura_e_edicao(self, session, tabela_taxas_repo):
        """Testa reabertura de tabela fechado e edição subsequente."""
        # Cria e finaliza uma tabela
        tabela = tabela_taxas_repo.criar(mes=1, ano=2024)
        tabela_taxas_repo.finalizar(tabela.id)

        tabela_fechada = tabela_taxas_repo.buscar_por_id(tabela.id)
        assert tabela_fechada.estado == EstadoDocumento.FECHADO

        # Reabre a tabela
        tabela_reaberta = tabela_taxas_repo.reabrir(tabela.id, "Correção de dados")
        assert tabela_reaberta.estado == EstadoDocumento.RASCUNHO
        assert tabela_reaberta.reopen_count == 1


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

    def test_criacao_conjunta_de_tabelas(self, session, tabela_taxas_repo, mapa_taxas_repo):
        """Testa criação de tabelas de taxas e taxas para o mesmo período."""
        mes, ano = 1, 2024

        # Cria tabela de taxas
        tabela_taxas = tabela_taxas_repo.criar(mes=mes, ano=ano)
        tabela_taxas_repo.adicionar_dia(tabela_taxas.id, 1, "Segunda-feira")

        # Cria mapa de taxas
        mapa_taxas = mapa_taxas_repo.criar(mes=mes, ano=ano)
        mapa_taxas_repo.adicionar_linha(mapa_taxas.id, 1, 100, Decimal("100.0"))

        # Verifica ambas as tabelas
        assert tabela_taxas.mes == mes
        assert tabela_taxas.ano == ano
        assert mapa_taxas.mes == mes
        assert mapa_taxas.ano == ano

        # Busca por mês/ano deve retornar ambas
        tabela_taxas_encontrada = tabela_taxas_repo.buscar_por_mes_ano(mes, ano)
        mapa_taxas_encontrado = mapa_taxas_repo.buscar_por_mes_ano(mes, ano)

        assert tabela_taxas_encontrada.id == tabela_taxas.id
        assert mapa_taxas_encontrado.id == mapa_taxas.id

    def test_listagem_ordenada_de_tabelas(self, session, tabela_taxas_repo, mapa_taxas_repo):
        """Testa listagem ordenada de tabelas por data."""
        # Cria tabelas em ordem cronológica
        datas = [(1, 2024), (2, 2024), (12, 2023)]

        for mes, ano in datas:
            tabela_taxas_repo.criar(mes=mes, ano=ano)
            mapa_taxas_repo.criar(mes=mes, ano=ano)

        # Listagem deve ser ordenada por ano/mês descendente
        tabelas_taxas = tabela_taxas_repo.listar_todos()
        mapas_taxas = mapa_taxas_repo.listar_todos()

        assert len(tabelas_taxas) == 3
        assert len(mapas_taxas) == 3

        # Verifica ordem: (2, 2024), (1, 2024), (12, 2023)
        assert tabelas_taxas[0].mes == 2
        assert tabelas_taxas[0].ano == 2024
        assert tabelas_taxas[1].mes == 1
        assert tabelas_taxas[1].ano == 2024
        assert tabelas_taxas[2].mes == 12
        assert tabelas_taxas[2].ano == 2023


class TestErrosEExcecoes:
    """Testes para tratamento de erros e exceções."""

    def test_criacao_tabela_com_dados_invalidos(self, tabela_taxas_repo):
        """Testa criação de tabela com dados inválidos."""
        with pytest.raises(ValueError, match="Mês inválido"):
            tabela_taxas_repo.criar(mes=13, ano=2024)

        with pytest.raises(ValueError, match="Ano inválido"):
            tabela_taxas_repo.criar(mes=1, ano=1999)

    def test_operacoes_em_tabela_inexistente(self, tabela_taxas_repo):
        """Testa operações em tabela inexistente."""
        with pytest.raises(ValueError, match="não encontrado"):
            tabela_taxas_repo.buscar_por_id(999)

        with pytest.raises(ValueError, match="não encontrado"):
            tabela_taxas_repo.finalizar(999)

        with pytest.raises(ValueError, match="não encontrado"):
            tabela_taxas_repo.recalcular_totais(999)

    def test_adicao_de_dias_em_tabela_inexistente(self, tabela_taxas_repo):
        """Testa adição de dias em tabela inexistente."""
        with pytest.raises(ValueError, match="não encontrado"):
            tabela_taxas_repo.adicionar_dia(999, 1, "Segunda-feira")

    def test_finalizacao_de_tabela_ja_fechado(self, tabela_taxas_repo):
        """Testa finalização de tabela já fechado."""
        from src.common.execptions.assiduidade import TabelaTaxasInvalidStateError

        tabela = tabela_taxas_repo.criar(mes=1, ano=2024)
        tabela_taxas_repo.finalizar(tabela.id)

        with pytest.raises(TabelaTaxasInvalidStateError):
            tabela_taxas_repo.finalizar(tabela.id)
