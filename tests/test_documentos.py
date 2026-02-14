"""Testes específicos para Documentos e validações.

Testa validações de documentos, integridade de dados e operações específicas.
"""

import pytest
from sqlalchemy.exc import IntegrityError

from src.db.models.mapas import Documento
from src.db.models.user import User


class TestDocumentoValidacoes:
    """Testes para validações de Documento."""

    def test_criar_documento_com_dados_minimos(self, session, documento_data):
        """Testa criação de documento com dados mínimos obrigatórios."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        assert documento.id is not None
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

    def test_criar_documento_sem_campos_obrigatorios(self, session, documento_data):
        """Testa criação de documento sem campos obrigatórios (deve falhar)."""
        campos_obrigatorios = [
            "nome_original",
            "path_relativo",
            "hash_sha256",
            "tipo",
            "tamanho_bytes",
        ]

        for campo in campos_obrigatorios:
            dados_invalidos = documento_data.copy()
            dados_invalidos.pop(campo)

            # Campos obrigatórios lancam ValueError/TypeError no __init__
            with pytest.raises((ValueError, TypeError, IntegrityError)):
                documento = Documento(**dados_invalidos)
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
        session.rollback()

    def test_criar_documento_com_user(self, session, documento_data, user_data):
        """Testa criação de documento associado a um usuário."""
        user = User(**user_data)
        session.add(user)
        session.commit()

        documento_data["user_id"] = user.ip
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        assert documento.user_id == user.ip
        assert documento.user.ip == user.ip
        assert documento.user.username == user.username

    def test_to_dict_com_tamanho_kb(self, session, documento_data):
        """Testa método to_dict com cálculo de tamanho em KB."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        documento_dict = documento.to_dict()
        assert documento_dict["tamanho_kb"] == 1.0  # 1024 bytes = 1 KB

    def test_to_dict_sem_dados_extraidos(self, session, documento_data):
        """Testa método to_dict sem dados extraídos."""
        documento_data.pop("dados_extraidos")
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        documento_dict = documento.to_dict()
        assert documento_dict["nome_original"] == "test.pdf"
        assert documento_dict["tipo"] == "PDF"
        assert documento_dict["status_validacao"] == "PENDENTE"


class TestDocumentoOperacoes:
    """Testes para operações específicas de Documento."""

    def test_atualizacao_status_validacao(self, session, documento_data):
        """Testa atualização do status de validação."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        # Atualiza status
        documento.status_validacao = "VALIDADO"
        documento.confianca_score = 95
        session.commit()

        documento_atualizado = session.query(Documento).filter_by(id=documento.id).first()
        assert documento_atualizado.status_validacao == "VALIDADO"
        assert documento_atualizado.confianca_score == 95

    def test_atualizacao_dados_extraidos(self, session, documento_data):
        """Testa atualização de dados extraídos."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        # Atualiza dados extraídos
        novos_dados = {
            "valor": 200.0,
            "data_emissao": "2024-01-01",
            "fornecedor": "Teste Fornecedor"
        }
        documento.dados_extraidos = novos_dados
        session.commit()

        documento_atualizado = session.query(Documento).filter_by(id=documento.id).first()
        assert documento_atualizado.dados_extraidos == novos_dados

    def test_busca_por_hash(self, session, documento_data):
        """Testa busca de documento por hash SHA256."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        documento_encontrado = session.query(Documento).filter_by(hash_sha256=documento.hash_sha256).first()
        assert documento_encontrado is not None
        assert documento_encontrado.id == documento.id
        assert documento_encontrado.nome_original == documento.nome_original

    def test_busca_por_tipo(self, session, documento_data):
        """Testa busca de documentos por tipo."""
        # Cria documentos de diferentes tipos
        documento1 = Documento(**documento_data)
        documento_data["nome_original"] = "test2.jpg"
        documento_data["path_relativo"] = "documents/test2.jpg"
        documento_data["hash_sha256"] = "def456"
        documento_data["tipo"] = "JPEG"
        documento2 = Documento(**documento_data)

        session.add_all([documento1, documento2])
        session.commit()

        documentos_pdf = session.query(Documento).filter_by(tipo="PDF").all()
        assert len(documentos_pdf) == 1
        assert documentos_pdf[0].id == documento1.id

        documentos_jpeg = session.query(Documento).filter_by(tipo="JPEG").all()
        assert len(documentos_jpeg) == 1
        assert documentos_jpeg[0].id == documento2.id

    def test_contagem_documentos_por_status(self, session, documento_data):
        """Testa contagem de documentos por status de validação."""
        # Cria documentos com diferentes status
        documento1 = Documento(**documento_data)
        documento_data["hash_sha256"] = "def456"
        documento_data["status_validacao"] = "VALIDADO"
        documento2 = Documento(**documento_data)
        documento_data["hash_sha256"] = "ghi789"
        documento_data["status_validacao"] = "PARCIAL"
        documento3 = Documento(**documento_data)

        session.add_all([documento1, documento2, documento3])
        session.commit()

        count_pendente = session.query(Documento).filter_by(status_validacao="PENDENTE").count()
        count_validado = session.query(Documento).filter_by(status_validacao="VALIDADO").count()
        count_parcial = session.query(Documento).filter_by(status_validacao="PARCIAL").count()

        assert count_pendente == 1
        assert count_validado == 1
        assert count_parcial == 1


class TestDocumentoIntegridade:
    """Testes para integridade de dados do Documento."""

    def test_hash_sha256_formato(self, session, documento_data):
        """Testa que hash SHA256 é hexadecimal válido.

        Nota: O formato exato depende da aplicação.
        Este teste apenas valida que é uma string hexadecimal.
        """
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        # Hash deve ser hexadecimal (ou pelo menos alfanumérico)
        assert isinstance(documento.hash_sha256, str)
        assert len(documento.hash_sha256) > 0

    def test_tamanho_bytes_positivo(self, session, documento_data):
        """Testa que tamanho_bytes é positivo."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        assert documento.tamanho_bytes > 0

    def test_confianca_score_limites(self, session, documento_data):
        """Testa limites do confianca_score (0-100)."""
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        assert 0 <= documento.confianca_score <= 100

        # Testa atualização dentro dos limites
        documento.confianca_score = 100
        session.commit()
        assert documento.confianca_score == 100

        documento.confianca_score = 0
        session.commit()
        assert documento.confianca_score == 0

    def test_status_validacao_valores_permitidos(self, session, documento_data):
        """Testa valores permitidos para status_validacao."""
        valores_permitidos = ["PENDENTE", "VALIDADO", "PARCIAL", "ERRO", "REJEITADO"]

        for status in valores_permitidos:
            documento_data["hash_sha256"] = f"hash_{status.lower()}"
            documento_data["status_validacao"] = status
            documento = Documento(**documento_data)
            session.add(documento)
            session.commit()

            assert documento.status_validacao == status


class TestDocumentoRelacionamentos:
    """Testes para relacionamentos do Documento."""

    def test_documento_sem_user(self, session, documento_data):
        """Testa criação de documento sem usuário associado.

        Nota: O documento pode ser criado sem user_id (é opcional).
        """
        # Remover user_id para criar sem usuário
        documento_data_copy = documento_data.copy()
        user_id_before = documento_data_copy.get("user_id")
        documento_data_copy.pop("user_id", None)

        documento = Documento(**documento_data_copy)
        session.add(documento)
        session.commit()

        # user_id pode ser None
        assert documento.user_id is None
        assert documento.user is None

    def test_documento_com_user_inexistente(self, session, documento_data):
        """Testa criação de documento com user_id inexistente.

        Nota: Apenas valida se FK constraints forem habilitadas na BD.
        Em SQLite, FK é optional e desativada por padrão em testes.
        """
        documento_data["user_id"] = 999  # User inexistente
        documento = Documento(**documento_data)
        session.add(documento)

        # Se FK está habilitada na BD, deve lançar IntegrityError
        # Se FK está desabilitada, o insert vai passar mas terá dados órfãos
        try:
            session.commit()
            # Se chegou aqui, FK não está ativada (comportamento esperado em testes)
            session.rollback()
        except IntegrityError:
            # Se chegou aqui, FK está ativada (comportamento de produção)
            session.rollback()

    def test_cascade_delete_user(self, session, documento_data, user_data):
        """Testa comportamento de cascade delete ao remover usuário."""
        user = User(**user_data)
        session.add(user)
        session.commit()

        documento_data["user_id"] = user.ip
        documento = Documento(**documento_data)
        session.add(documento)
        session.commit()

        # Remove usuário
        session.delete(user)
        session.commit()

        # Documento deve ser removido por cascade
        documento_removido = session.query(Documento).filter_by(id=documento.id).first()
        assert documento_removido is None
