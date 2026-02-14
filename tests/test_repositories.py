"""Testes para os repositórios.

Testa operações CRUD, validações e lógica de negócios dos repositórios:
- MapaAssiduidadeRepository
- MapaTaxasRepository
"""

from decimal import Decimal

import pytest

from src.common.constants.enums import EstadoDocumento, TipoDiaAssiduidade


class TestMapaAssiduidadeRepository:
    """Testes para MapaAssiduidadeRepository."""

    def test_criar_mapa_assiduidade(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa criação de mapa de assiduidade."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)

        assert mapa.id is not None
        assert mapa.mes == 1
        assert mapa.ano == 2024
        assert mapa.estado == EstadoDocumento.RASCUNHO
        assert mapa.versao == 1
        assert mapa.wizard_data == {"stage": 1, "data": "test"}

    def test_criar_mapa_assiduidade_mes_invalido(self, mapa_assiduidade_repo):
        """Testa criação de mapa de assiduidade com mês inválido."""
        with pytest.raises(ValueError, match="Mês inválido"):
            mapa_assiduidade_repo.criar(mes=13, ano=2024)

    def test_criar_mapa_assiduidade_ano_invalido(self, mapa_assiduidade_repo):
        """Testa criação de mapa de assiduidade com ano inválido."""
        with pytest.raises(ValueError, match="Ano inválido"):
            mapa_assiduidade_repo.criar(mes=1, ano=1999)

    def test_buscar_por_id(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa busca de mapa por ID."""
        mapa_criado = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        mapa_encontrado = mapa_assiduidade_repo.buscar_por_id(mapa_criado.id)

        assert mapa_encontrado is not None
        assert mapa_encontrado.id == mapa_criado.id
        assert mapa_encontrado.mes == mapa_criado.mes
        assert mapa_encontrado.ano == mapa_criado.ano

    def test_buscar_por_id_nao_encontrado(self, mapa_assiduidade_repo):
        """Testa busca de mapa por ID inexistente."""
        mapa = mapa_assiduidade_repo.buscar_por_id(999)
        assert mapa is None

    def test_buscar_por_mes_ano(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa busca de mapa por mês/ano."""
        mapa_criado = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        mapa_encontrado = mapa_assiduidade_repo.buscar_por_mes_ano(1, 2024)

        assert mapa_encontrado is not None
        assert mapa_encontrado.id == mapa_criado.id
        assert mapa_encontrado.mes == 1
        assert mapa_encontrado.ano == 2024

    def test_buscar_por_mes_ano_nao_encontrado(self, mapa_assiduidade_repo):
        """Testa busca de mapa por mês/ano inexistente."""
        mapa = mapa_assiduidade_repo.buscar_por_mes_ano(1, 2024)
        assert mapa is None

    def test_atualizar_mapa(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa atualização de mapa."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        mapa.wizard_data = {"stage": 2, "data": "updated"}
        mapa_assiduidade_repo.atualizar(mapa)

        mapa_atualizado = mapa_assiduidade_repo.buscar_por_id(mapa.id)
        assert mapa_atualizado.wizard_data == {"stage": 2, "data": "updated"}

    def test_eliminar_mapa(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa eliminação de mapa."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        assert mapa_assiduidade_repo.eliminar(mapa.id) is True
        assert mapa_assiduidade_repo.buscar_por_id(mapa.id) is None

    def test_eliminar_mapa_nao_encontrado(self, mapa_assiduidade_repo):
        """Testa eliminação de mapa inexistente."""
        assert mapa_assiduidade_repo.eliminar(999) is False

    def test_listar_todos(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa listagem de todos os mapas."""
        mapa1 = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        mapa_assiduidade_data["mes"] = 2
        mapa2 = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)

        mapas = mapa_assiduidade_repo.listar_todos()
        assert len(mapas) == 2
        assert mapas[0].id == mapa2.id  # Ordenado por ano/mês descendente
        assert mapas[1].id == mapa1.id

    def test_adicionar_dia(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa adição de dia ao mapa."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)

        linha = mapa_assiduidade_repo.adicionar_dia(
            mapa_id=mapa.id,
            dia=1,
            dia_semana="Segunda-feira",
            tipo=TipoDiaAssiduidade.TRABALHO,
            ips=8,
            valor_sem_iva=Decimal("50.0"),
            km=Decimal("50.0"),
        )

        assert linha.id is not None
        assert linha.mapa_id == mapa.id
        assert linha.dia == 1
        assert linha.dia_semana == "Segunda-feira"
        assert linha.tipo == TipoDiaAssiduidade.TRABALHO
        assert linha.ips == 8
        assert linha.valor_sem_iva == Decimal("50.0")
        assert linha.km == Decimal("50.0")

    def test_adicionar_dias_bulk(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa adição de múltiplos dias ao mapa."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)

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
        ]

        linhas = mapa_assiduidade_repo.adicionar_dias_bulk(mapa.id, dias_data)
        assert len(linhas) == 2

        # Verifica a primeira linha
        assert linhas[0].dia == 1
        assert linhas[0].tipo == TipoDiaAssiduidade.TRABALHO
        assert linhas[0].ips == 8
        assert linhas[0].valor_sem_iva == Decimal("50.0")

        # Verifica a segunda linha
        assert linhas[1].dia == 2
        assert linhas[1].tipo == TipoDiaAssiduidade.AUSENCIA
        assert linhas[1].motivo == "Doença"

    def test_limpar_dias(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa limpeza de todos os dias de um mapa."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)

        # Adiciona dias
        mapa_assiduidade_repo.adicionar_dia(mapa.id, 1, "Segunda-feira")
        mapa_assiduidade_repo.adicionar_dia(mapa.id, 2, "Terça-feira")

        # Limpa dias
        count = mapa_assiduidade_repo.limpar_dias(mapa.id)
        assert count == 2

        # Verifica que não há mais linhas
        mapa_atualizado = mapa_assiduidade_repo.buscar_por_id(mapa.id)
        assert len(mapa_atualizado.linhas) == 0

    def test_finalizar_mapa(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa finalização de mapa."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        mapa_finalizado = mapa_assiduidade_repo.finalizar(mapa.id)

        assert mapa_finalizado.estado == EstadoDocumento.FECHADO
        assert mapa_finalizado.finalizado_em is not None
        assert mapa_finalizado.fechado_em is not None

    def test_finalizar_mapa_ja_fechado(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa finalização de mapa já fechado."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)
        mapa_assiduidade_repo.finalizar(mapa.id)

        # Tentar finalizar novamente deve lançar erro
        with pytest.raises(Exception):  # Pode ser InvalidStateError ou ValueError
            mapa_assiduidade_repo.finalizar(mapa.id)

    def test_recalcular_totais(self, mapa_assiduidade_repo, mapa_assiduidade_data):
        """Testa recálculo de totais a partir das linhas."""
        mapa = mapa_assiduidade_repo.criar(**mapa_assiduidade_data)

        # Adiciona linhas de teste
        mapa_assiduidade_repo.adicionar_dia(
            mapa.id, 1, "Segunda-feira", TipoDiaAssiduidade.TRABALHO,
            ips=8, valor_sem_iva=Decimal("50.0"), km=Decimal("50.0")
        )
        mapa_assiduidade_repo.adicionar_dia(
            mapa.id, 2, "Terça-feira", TipoDiaAssiduidade.AUSENCIA, motivo="Doença"
        )
        mapa_assiduidade_repo.adicionar_dia(
            mapa.id, 3, "Quarta-feira", TipoDiaAssiduidade.FERIAS
        )

        mapa_atualizado = mapa_assiduidade_repo.recalcular_totais(mapa.id)

        assert mapa_atualizado.total_dias_trabalho == 1
        assert mapa_atualizado.total_km == Decimal("50.0")
        assert mapa_atualizado.total_ips == 8
        assert mapa_atualizado.total_faturacao == Decimal("50.0")
        assert mapa_atualizado.total_ausencias == 1
        assert mapa_atualizado.total_ferias == 1
        assert mapa_atualizado.total_feriados == 0


class TestMapaTaxasRepository:
    """Testes para MapaTaxasRepository."""

    def test_criar_mapa_taxas(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa criação de mapa de taxas."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)

        assert mapa.id is not None
        assert mapa.mes == 1
        assert mapa.ano == 2024
        assert mapa.estado == EstadoDocumento.RASCUNHO
        assert mapa.versao == 1
        assert mapa.wizard_data == {"stage": 2, "data": "test"}

    def test_buscar_por_id(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa busca de mapa por ID."""
        mapa_criado = mapa_taxas_repo.criar(**mapa_taxas_data)
        mapa_encontrado = mapa_taxas_repo.buscar_por_id(mapa_criado.id)

        assert mapa_encontrado is not None
        assert mapa_encontrado.id == mapa_criado.id
        assert mapa_encontrado.mes == mapa_criado.mes
        assert mapa_encontrado.ano == mapa_criado.ano

    def test_buscar_por_mes_ano(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa busca de mapa por mês/ano."""
        mapa_criado = mapa_taxas_repo.criar(**mapa_taxas_data)
        mapa_encontrado = mapa_taxas_repo.buscar_por_mes_ano(1, 2024)

        assert mapa_encontrado is not None
        assert mapa_encontrado.id == mapa_criado.id
        assert mapa_encontrado.mes == 1
        assert mapa_encontrado.ano == 2024

    def test_adicionar_linha(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa adição de linha ao mapa."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)

        linha = mapa_taxas_repo.adicionar_linha(
            mapa_id=mapa.id,
            ordem=1,
            recibo=100,
            setubal=Decimal("100.0"),
            santarem=Decimal("50.0"),
            evora=Decimal("25.0"),
            ips=8,
            dividas=Decimal("10.0"),
        )

        assert linha.id is not None
        assert linha.mapa_id == mapa.id
        assert linha.ordem == 1
        assert linha.recibo == 100
        assert linha.setubal == Decimal("100.0")
        assert linha.santarem == Decimal("50.0")
        assert linha.evora == Decimal("25.0")
        assert linha.ips == 8
        assert linha.dividas == Decimal("10.0")
        assert linha.total_faturacao == Decimal("175.0")

    def test_adicionar_linhas_bulk(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa adição de múltiplas linhas ao mapa."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)

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

        # Verifica a primeira linha
        assert linhas[0].ordem == 1
        assert linhas[0].recibo == 100
        assert linhas[0].setubal == Decimal("100.0")
        assert linhas[0].santarem == Decimal("50.0")
        assert linhas[0].evora == Decimal("25.0")
        assert linhas[0].ips == 8
        assert linhas[0].dividas == Decimal("10.0")

        # Verifica a segunda linha
        assert linhas[1].ordem == 2
        assert linhas[1].recibo == 101
        assert linhas[1].setubal == Decimal("200.0")
        assert linhas[1].santarem == Decimal("100.0")
        assert linhas[1].evora == Decimal("50.0")
        assert linhas[1].ips == 16
        assert linhas[1].dividas == Decimal("20.0")

    def test_limpar_linhas(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa limpeza de todas as linhas de um mapa."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)

        # Adiciona linhas
        mapa_taxas_repo.adicionar_linha(mapa.id, 1, 100, Decimal("100.0"))
        mapa_taxas_repo.adicionar_linha(mapa.id, 2, 101, Decimal("200.0"))

        # Limpa linhas
        count = mapa_taxas_repo.limpar_linhas(mapa.id)
        assert count == 2

        # Verifica que não há mais linhas
        mapa_atualizado = mapa_taxas_repo.buscar_por_id(mapa.id)
        assert len(mapa_atualizado.linhas) == 0

    def test_calcular_totais(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa cálculo de totais a partir das linhas."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)

        # Adiciona linhas de teste
        mapa_taxas_repo.adicionar_linha(
            mapa.id, 1, 100, Decimal("100.0"), Decimal("50.0"), Decimal("25.0"), 8, Decimal("10.0")
        )
        mapa_taxas_repo.adicionar_linha(
            mapa.id, 2, 101, Decimal("200.0"), Decimal("100.0"), Decimal("50.0"), 16, Decimal("20.0")
        )

        mapa_atualizado = mapa_taxas_repo.calcular_totais(mapa.id)

        assert mapa_atualizado.total_setubal == Decimal("300.0")
        assert mapa_atualizado.total_santarem == Decimal("150.0")
        assert mapa_atualizado.total_evora == Decimal("75.0")
        assert mapa_atualizado.total_ips == 24
        assert mapa_atualizado.total_dividas == Decimal("30.0")
        assert mapa_atualizado.total_faturacao == Decimal("525.0")

    def test_finalizar_mapa(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa finalização de mapa."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)
        mapa_finalizado = mapa_taxas_repo.finalizar(mapa.id)

        assert mapa_finalizado.estado == EstadoDocumento.FECHADO
        assert mapa_finalizado.finalizado_em is not None
        assert mapa_finalizado.fechado_em is not None

    def test_atualizar_pdf_path(self, mapa_taxas_repo, mapa_taxas_data):
        """Testa atualização do caminho do PDF."""
        mapa = mapa_taxas_repo.criar(**mapa_taxas_data)
        mapa_atualizado = mapa_taxas_repo.atualizar_pdf_path(mapa.id, "/path/to/pdf.pdf")

        assert mapa_atualizado.pdf_path == "/path/to/pdf.pdf"
