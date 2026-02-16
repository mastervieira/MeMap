"""Testes para os modelos de banco de dados.

Testa validação, criação, relacionamentos e métodos dos modelos:
- User
- Documento
- TabelaTaxas
- TabelaTaxasLinha
- MapaTaxas
- MapaTaxasLinha
"""

from decimal import Decimal

import pytest
from sqlalchemy.exc import IntegrityError

from src.common.constants.enums import (
    EstadoDocumento,
    TipoDiaAssiduidade,
    UserRole,
)
from src.db.models.mapas import (
    Documento,
    TabelaTaxas,
    TabelaTaxasLinha,
    MapaTaxas,
    MapaTaxasLinha,
)
from src.db.models.user import User


class TestUser:
    """Testes para o modelo User."""

    def test_criar_usuario_valido(self, session, user_data):
        """Testa criação de usuário com dados válidos."""
        user = User(**user_data)
        session.add(user)
        session.commit()

        assert user.ip == 1
        assert user.username == "test_user"
        assert user.password_hash == "hashed_password"
        assert user.modo_bd == UserRole.TECNICO
        assert user.ativo is True
        assert user.nome_completo == "Test User"
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_criar_usuario_sem_username(self, session, user_data):
        """Testa criação de usuário sem username (deve falhar)."""
        user_data.pop("username")
        user = User(**user_data)

        session.add(user)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_criar_usuario_username_duplicado(self, session, user_data):
        """Testa criação de usuário com username duplicado (deve falhar)."""
        user1 = User(**user_data)
        session.add(user1)
        session.commit()

        user2 = User(**user_data)
        session.add(user2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_to_dict(self, session, user_data):
        """Testa método to_dict do User."""
        user = User(**user_data)
        session.add(user)
        session.commit()

        user_dict = user.to_dict()
        assert user_dict["ip"] == 1
        assert user_dict["username"] == "test_user"
        assert user_dict["modo_bd"] == "TECNICO"
        assert user_dict["ativo"] is True


class TestDocumento:
    """Testes para o modelo Documento."""

    def test_criar_documento_valido(self, session, documento_data):
        """Testa criação de documento com dados válidos."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        assert documento.nome_original == "test.pdf"
        assert documento.path_relativo == "documents/test.pdf"
        assert documento.hash_sha256 == "abc123"
        assert documento.tipo == "PDF"
        assert documento.tamanho_bytes == 1024
        assert documento.status_validacao == "PENDENTE"
        assert documento.confianca_score == 85
        assert documento.dados_extraidos == {"valor": 100.0}
        assert documento.created_at is not None
        assert documento.updated_at is not None

    def test_criar_documento_sem_nome(self, session, documento_data):
        """Testa criação de documento sem nome (deve falhar)."""
        documento_data.pop("nome_original")

        # ValueError/TypeError é lançado no __init__ quando falta nome_original
        with pytest.raises((ValueError, TypeError, IntegrityError)):
            documento = Documento(**documento_data)
            session.add(documento)
            session.commit()

    def test_criar_documento_hash_duplicado(self, session, documento_data):
        """Testa criação de documento com hash duplicado (deve falhar)."""
        documento1 = Documento(**documento_data)
        session.add(documento1)
        session.commit()

        documento2 = Documento(**documento_data)
        session.add(documento2)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_to_dict(self, session, documento_data):
        """Testa método to_dict do Documento."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        documento_dict = documento.to_dict()
        assert documento_dict["nome_original"] == "test.pdf"
        assert documento_dict["tipo"] == "PDF"
        assert documento_dict["tamanho_kb"] == 1.0
        assert documento_dict["status_validacao"] == "PENDENTE"
        assert documento_dict["confianca_score"] == 85


class TestTabelaTaxas:
    """Testes para o modelo TabelaTaxas."""

    def test_criar_tabela_taxas_valido(self, session, tabela_taxas_data):
        """Testa criação de tabela de taxas com dados válidos."""
        tabela = TabelaTaxas(**tabela_taxas_data)
        session.add(tabela)
        session.commit()

        assert tabela.mes == 1
        assert tabela.ano == 2024
        assert tabela.estado == EstadoDocumento.RASCUNHO
        assert tabela.versao == 1
        assert tabela.wizard_data == {"stage": 1, "data": "test"}
        assert tabela.created_at is not None
        assert tabela.updated_at is not None
        assert tabela.total_dias_trabalho == 0
        assert tabela.total_km == Decimal("0")
        assert tabela.total_ips == 0
        assert tabela.total_faturacao == Decimal("0")
        assert tabela.total_ausencias == 0
        assert tabela.total_ferias == 0
        assert tabela.total_feriados == 0

    def test_criar_tabela_taxas_sem_mes(self, session, tabela_taxas_data):
        """Testa criação de tabela de taxas sem mes (deve falhar)."""
        tabela_taxas_data.pop("mes")
        tabela = TabelaTaxas(**tabela_taxas_data)

        session.add(tabela)
        with pytest.raises(IntegrityError):
            session.commit()

    def test_criar_tabela_taxas_mes_invalido(self, session, tabela_taxas_data):
        """Testa criação de tabela de taxas com mes inválido.

        Nota: A validação de mes/ano é feita no repository,
        não no modelo. Este teste apenas verifica que o modelo
        aceita o valor (validação é de negócio, não de BD).
        """
        tabela_taxas_data["mes"] = 13
        tabela = TabelaTaxas(**tabela_taxas_data)

        session.add(tabela)
        # Modelo aceita, validação é no repository
        session.commit()

    def test_calcular_totais(self, session, tabela_taxas_data):
        """Testa cálculo de totais a partir das linhas."""
        tabela = TabelaTaxas(**tabela_taxas_data)
        session.add(tabela)
        session.commit()

        # Adiciona linhas de teste
        linha1 = TabelaTaxasLinha(
            mapa_id=tabela.id,
            dia=1,
            dia_semana="Segunda-feira",
            tipo=TipoDiaAssiduidade.TRABALHO,
            ips=8,
            valor_com_iva=Decimal("50.0"),
            km=Decimal("50.0"),
        )
        linha2 = TabelaTaxasLinha(
            mapa_id=tabela.id,
            dia=2,
            dia_semana="Terça-feira",
            tipo=TipoDiaAssiduidade.AUSENCIA,
            motivo="Doença",
        )
        linha3 = TabelaTaxasLinha(
            mapa_id=tabela.id,
            dia=3,
            dia_semana="Quarta-feira",
            tipo=TipoDiaAssiduidade.FERIAS,
        )

        session.add_all([linha1, linha2, linha3])
        session.commit()

        # Recalcula totais
        tabela.recalcular_totais()

        assert tabela.total_dias_trabalho == 1
        assert tabela.total_km == Decimal("50.0")
        assert tabela.total_ips == 8
        assert tabela.total_faturacao == Decimal("50.0")
        assert tabela.total_ausencias == 1
        assert tabela.total_ferias == 1
        assert tabela.total_feriados == 0


class TestTabelaTaxasLinha:
    """Testes para o modelo TabelaTaxasLinha."""

    def test_criar_linha_taxas_valida(self, session, tabela_taxas_data):
        """Testa criação de linha de taxas com dados válidos."""
        tabela = TabelaTaxas(**tabela_taxas_data)
        session.add(tabela)
        session.commit()

        linha = TabelaTaxasLinha(
            mapa_id=tabela.id,
            dia=1,
            dia_semana="Segunda-feira",
            tipo=TipoDiaAssiduidade.TRABALHO,
            recibo_inicio=100,
            recibo_fim=101,
            ips=8,
            valor_com_iva=Decimal("50.0"),
            locais="Lisboa",
            km=Decimal("50.0"),
            observacoes="Teste",
        )
        session.add(linha)
        session.commit()

        assert linha.mapa_id == tabela.id
        assert linha.dia == 1
        assert linha.dia_semana == "Segunda-feira"
        assert linha.tipo == TipoDiaAssiduidade.TRABALHO
        assert linha.recibo_inicio == 100
        assert linha.recibo_fim == 101
        assert linha.ips == 8
        assert linha.valor_com_iva == Decimal("50.0")
        assert linha.locais == "Lisboa"
        assert linha.km == Decimal("50.0")
        assert linha.observacoes == "Teste"

    def test_criar_linha_taxas_sem_tabela_id(self, session):
        """Testa criação de linha de taxas sem tabela_id (deve falhar)."""
        linha = TabelaTaxasLinha(
            dia=1,
            dia_semana="Segunda-feira",
            tipo=TipoDiaAssiduidade.TRABALHO,
        )

        session.add(linha)
        with pytest.raises(IntegrityError):
            session.commit()


class TestMapaTaxas:
    """Testes para o modelo MapaTaxas."""

    def test_criar_mapa_taxas_valido(self, session, mapa_taxas_data):
        """Testa criação de mapa de taxas com dados válidos."""
        mapa = MapaTaxas(**mapa_taxas_data)
        session.add(mapa)
        session.commit()

        assert mapa.mes == 1
        assert mapa.ano == 2024
        assert mapa.estado == EstadoDocumento.RASCUNHO
        assert mapa.versao == 1
        assert mapa.wizard_data == {"stage": 2, "data": "test"}
        assert mapa.created_at is not None
        assert mapa.updated_at is not None
        assert mapa.total_setubal == Decimal("0")
        assert mapa.total_santarem == Decimal("0")
        assert mapa.total_evora == Decimal("0")
        assert mapa.total_ips == 0
        assert mapa.total_dividas == Decimal("0")
        assert mapa.total_faturacao == Decimal("0")

    def test_calcular_totais(self, session, mapa_taxas_data):
        """Testa cálculo de totais a partir das linhas."""
        mapa = MapaTaxas(**mapa_taxas_data)
        session.add(mapa)
        session.commit()

        # Adiciona linhas de teste
        linha1 = MapaTaxasLinha(
            mapa_id=mapa.id,
            ordem=1,
            recibo=100,
            setubal=Decimal("100.0"),
            santarem=Decimal("50.0"),
            evora=Decimal("25.0"),
            ips=8,
            dividas=Decimal("10.0"),
        )
        linha2 = MapaTaxasLinha(
            mapa_id=mapa.id,
            ordem=2,
            recibo=101,
            setubal=Decimal("200.0"),
            santarem=Decimal("100.0"),
            evora=Decimal("50.0"),
            ips=16,
            dividas=Decimal("20.0"),
        )

        session.add_all([linha1, linha2])
        session.commit()

        # Recalcula totais
        mapa.calcular_totais()

        assert mapa.total_setubal == Decimal("300.0")
        assert mapa.total_santarem == Decimal("150.0")
        assert mapa.total_evora == Decimal("75.0")
        assert mapa.total_ips == 24
        assert mapa.total_dividas == Decimal("30.0")
        assert mapa.total_faturacao == Decimal("525.0")


class TestMapaTaxasLinha:
    """Testes para o modelo MapaTaxasLinha."""

    def test_criar_linha_taxas_valida(self, session, mapa_taxas_data):
        """Testa criação de linha de taxas com dados válidos."""
        mapa = MapaTaxas(**mapa_taxas_data)
        session.add(mapa)
        session.commit()

        linha = MapaTaxasLinha(
            mapa_id=mapa.id,
            ordem=1,
            recibo=100,
            setubal=Decimal("100.0"),
            santarem=Decimal("50.0"),
            evora=Decimal("25.0"),
            ips=8,
            dividas=Decimal("10.0"),
        )
        session.add(linha)
        session.commit()

        assert linha.mapa_id == mapa.id
        assert linha.ordem == 1
        assert linha.recibo == 100
        assert linha.setubal == Decimal("100.0")
        assert linha.santarem == Decimal("50.0")
        assert linha.evora == Decimal("25.0")
        assert linha.ips == 8
        assert linha.dividas == Decimal("10.0")
        assert linha.total_faturacao == Decimal("175.0")

    def test_criar_linha_taxas_sem_mapa_id(self, session):
        """Testa criação de linha de taxas sem mapa_id (deve falhar)."""
        linha = MapaTaxasLinha(
            ordem=1,
            recibo=100,
            setubal=Decimal("100.0"),
        )

        session.add(linha)
        with pytest.raises(IntegrityError):
            session.commit()
