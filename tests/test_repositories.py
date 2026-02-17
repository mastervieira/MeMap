# type: ignore

"""Testes para os repositórios.

Testa operações CRUD, validações e lógica de negócios dos repositórios:
- TabelaTaxasRepository
- MapaTaxasRepository
"""

from decimal import Decimal

import pytest

from src.common.constants.enums import EstadoDocumento, TipoDiaAssiduidade


class TestTabelaTaxasRepository:
    """Testes para TabelaTaxasRepository."""

    def test_criar_tabela_taxas(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa criação de tabela de taxas."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)

        assert tabela.id is not None
        assert tabela.mes == 1
        assert tabela.ano == 2024
        assert tabela.estado == EstadoDocumento.RASCUNHO
        assert tabela.versao == 1
        assert tabela.wizard_data == {"stage": 1, "data": "test"}

    def test_criar_tabela_taxas_mes_invalido(self, tabela_taxas_repo):
        """Testa criação de tabela de taxas com mês inválido."""
        with pytest.raises(ValueError, match="Mês inválido"):
            tabela_taxas_repo.criar(mes=13, ano=2024)

    def test_criar_tabela_taxas_ano_invalido(self, tabela_taxas_repo):
        """Testa criação de tabela de taxas com ano inválido."""
        with pytest.raises(ValueError, match="Ano inválido"):
            tabela_taxas_repo.criar(mes=1, ano=1999)

    def test_buscar_por_id(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa busca de tabela por ID."""
        tabela_criada = tabela_taxas_repo.criar(**tabela_taxas_data)
        tabela_encontrada = tabela_taxas_repo.buscar_por_id(tabela_criada.id)

        assert tabela_encontrada is not None
        assert tabela_encontrada.id == tabela_criada.id
        assert tabela_encontrada.mes == tabela_criada.mes
        assert tabela_encontrada.ano == tabela_criada.ano

    def test_buscar_por_id_nao_encontrado(self, tabela_taxas_repo):
        """Testa busca de tabela por ID inexistente."""
        with pytest.raises(ValueError, match="não encontrado"):
            tabela_taxas_repo.buscar_por_id(999)

    def test_buscar_por_mes_ano(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa busca de tabela por mês/ano."""
        tabela_criada = tabela_taxas_repo.criar(**tabela_taxas_data)
        tabela_encontrada = tabela_taxas_repo.buscar_por_mes_ano(1, 2024)

        assert tabela_encontrada is not None
        assert tabela_encontrada.id == tabela_criada.id
        assert tabela_encontrada.mes == 1
        assert tabela_encontrada.ano == 2024

    def test_buscar_por_mes_ano_nao_encontrado(self, tabela_taxas_repo):
        """Testa busca de tabela por mês/ano inexistente."""
        tabela = tabela_taxas_repo.buscar_por_mes_ano(1, 2024)
        assert tabela is None

    def test_atualizar_tabela(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa atualização de tabela."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)
        tabela.wizard_data = {"stage": 2, "data": "updated"}
        tabela_taxas_repo.atualizar(tabela)

        tabela_atualizada = tabela_taxas_repo.buscar_por_id(tabela.id)
        assert tabela_atualizada.wizard_data == {"stage": 2, "data": "updated"}

    def test_eliminar_tabela(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa eliminação de tabela."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)
        assert tabela_taxas_repo.eliminar(tabela.id) is True

        # Após eliminar, deve lançar ValueError
        with pytest.raises(ValueError, match="não encontrado"):
            tabela_taxas_repo.buscar_por_id(tabela.id)

    def test_eliminar_tabela_nao_encontrado(self, tabela_taxas_repo):
        """Testa eliminação de tabela inexistente."""
        assert tabela_taxas_repo.eliminar(999) is False

    def test_listar_todos(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa listagem de todos as tabelas."""
        tabela1 = tabela_taxas_repo.criar(**tabela_taxas_data)
        tabela_taxas_data["mes"] = 2
        tabela2 = tabela_taxas_repo.criar(**tabela_taxas_data)

        tabelas = tabela_taxas_repo.listar_todos()
        assert len(tabelas) == 2
        assert tabelas[0].id == tabela2.id  # Ordenado por ano/mês descendente
        assert tabelas[1].id == tabela1.id

    def test_adicionar_dia(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa adição de dia à tabela."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)

        linha = tabela_taxas_repo.adicionar_dia(
            mapa_id=tabela.id,
            dia=1,
            dia_semana="Segunda-feira",
            tipo=TipoDiaAssiduidade.TRABALHO,
            ips=8,
            valor_com_iva=Decimal("50.0"),
            km=Decimal("50.0"),
        )

        assert linha.id is not None
        assert linha.mapa_id == tabela.id
        assert linha.dia == 1
        assert linha.dia_semana == "Segunda-feira"
        assert linha.tipo == TipoDiaAssiduidade.TRABALHO
        assert linha.ips == 8
        assert linha.valor_com_iva == Decimal("50.0")
        assert linha.km == Decimal("50.0")

    def test_adicionar_dias_bulk(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa adição de múltiplos dias à tabela."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)

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
        ]

        linhas = tabela_taxas_repo.adicionar_dias_bulk(tabela.id, dias_data)
        assert len(linhas) == 2

        # Verifica a primeira linha
        assert linhas[0].dia == 1
        assert linhas[0].tipo == TipoDiaAssiduidade.TRABALHO
        assert linhas[0].ips == 8
        assert linhas[0].valor_com_iva == Decimal("50.0")

        # Verifica a segunda linha
        assert linhas[1].dia == 2
        assert linhas[1].tipo == TipoDiaAssiduidade.AUSENCIA
        assert linhas[1].motivo == "Doença"

    def test_limpar_dias(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa limpeza de todos os dias de uma tabela."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)

        # Adiciona dias
        tabela_taxas_repo.adicionar_dia(tabela.id, 1, "Segunda-feira")
        tabela_taxas_repo.adicionar_dia(tabela.id, 2, "Terça-feira")

        # Limpa dias
        count = tabela_taxas_repo.limpar_dias(tabela.id)
        assert count == 2

        # Verifica que não há mais linhas
        tabela_atualizada = tabela_taxas_repo.buscar_por_id(tabela.id)
        assert len(tabela_atualizada.linhas) == 0

    def test_finalizar_tabela(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa finalização de tabela."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)
        tabela_finalizada = tabela_taxas_repo.finalizar(tabela.id)

        assert tabela_finalizada.estado == EstadoDocumento.FECHADO
        assert tabela_finalizada.finalizado_em is not None
        assert tabela_finalizada.fechado_em is not None

    def test_finalizar_tabela_ja_fechado(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa finalização de tabela já fechado."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)
        tabela_taxas_repo.finalizar(tabela.id)

        # Tentar finalizar novamente deve lançar erro
        with pytest.raises(Exception):  # Pode ser InvalidStateError ou ValueError
            tabela_taxas_repo.finalizar(tabela.id)

    def test_recalcular_totais(self, tabela_taxas_repo, tabela_taxas_data):
        """Testa recálculo de totais a partir das linhas."""
        tabela = tabela_taxas_repo.criar(**tabela_taxas_data)

        # Recalcula totais de uma tabela vazia
        tabela_atualizada = tabela_taxas_repo.recalcular_totais(tabela.id)

        # Deve ter totais zerados
        assert tabela_atualizada.total_dias_trabalho == 0
        assert tabela_atualizada.total_km == Decimal("0.0")
        assert tabela_atualizada.total_ips == 0
        assert tabela_atualizada.total_faturacao == Decimal("0.0")
        assert tabela_atualizada.total_ausencias == 0
        assert tabela_atualizada.total_ferias == 0
        assert tabela_atualizada.total_feriados == 0


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
