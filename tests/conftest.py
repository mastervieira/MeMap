"""Pytest configuration and shared fixtures."""

import sys
from pathlib import Path

# Add src/ to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.db.models.base_mixin import EstadoDocumento
from src.repositories.assiduidade_repository import MapaAssiduidadeRepository
from src.repositories.taxas_repositorie import MapaTaxasRepository


@pytest.fixture
def mapa_assiduidade_data():
    """Dados de teste para MapaAssiduidade."""
    return {
        "mes": 1,
        "ano": 2024,
        "estado": EstadoDocumento.RASCUNHO,
        "versao": 1,
        "wizard_data": {"stage": 1, "data": "test"},
        "total_dias_trabalho": 0,
        "total_km": Decimal("0.0"),
        "total_ips": 0,
        "total_faturacao": Decimal("0.0"),
        "total_ausencias": 0,
        "total_ferias": 0,
        "total_feriados": 0,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def mapa_assiduidade_repo(session):
    """Repositório de mapa de assiduidade para testes."""
    return MapaAssiduidadeRepository(session)


@pytest.fixture
def mapa_taxas_data():
    """Dados de teste para MapaTaxas."""
    return {
        "mes": 1,
        "ano": 2024,
        "estado": EstadoDocumento.RASCUNHO,
        "versao": 1,
        "wizard_data": {"stage": 2, "data": "test"},
        "total_setubal": Decimal("0.0"),
        "total_santarem": Decimal("0.0"),
        "total_evora": Decimal("0.0"),
        "total_ips": 0,
        "total_dividas": Decimal("0.0"),
        "total_faturacao": Decimal("0.0"),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def mapa_taxas_repo(session):
    """Repositório de mapa de taxas para testes."""
    return MapaTaxasRepository(session)


@pytest.fixture
def user_data():
    """Dados de teste para User."""
    from src.db.models.user import UserRole
    return {
        "ip": 1,
        "username": "test_user",
        "password_hash": "hashed_password",
        "nome_completo": "Test User",
        "modo_bd": UserRole.TECNICO,
        "ativo": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }
@pytest.fixture
def user(session, request):
    """Cria um User para os testes com IP dinâmico para evitar colisões."""
    from src.db.models.user import User, UserRole

    # Gera um IP único baseado no teste
    # Usa o índice do teste para evitar colisões
    test_index = getattr(request, "_pyfuncitem", None)
    ip_value = hash(str(test_index)) % 1000 + 100  # Range 100-1099

    user = User(
        ip=ip_value,
        username=f"test_user_{ip_value}",
        password_hash="hashed_password",
        nome_completo=f"Test User {ip_value}",
        modo_bd=UserRole.TECNICO,
        ativo=True,
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def documento_data(user):
    """Dados de teste para Documento."""
    return {
        "nome_original": "test.pdf",
        "path_relativo": "documents/test.pdf",
        "hash_sha256": "abc123",
        "tipo": "PDF",
        "tamanho_bytes": 1024,
        "user_id": user.ip,
        "status_validacao": "PENDENTE",
        "dados_extraidos": {"valor": 100.0},
        "confianca_score": 85,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }


@pytest.fixture
def session():
    """Session real do SQLAlchemy para testes.

    Usa SQLite em memória para testes rápidos.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from src.db.models.base_mixin import Base

    # Criar engine em memória
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        echo=False,
        pool_pre_ping=True,
    )

    # Ativar foreign keys no SQLite (pode causar issues com isolamento de transações)
    # @event.listens_for(engine, "connect")
    # def set_sqlite_pragma(dbapi_connection, connection_record):
    #     cursor = dbapi_connection.cursor()
    #     cursor.execute("PRAGMA foreign_keys=ON")
    #     cursor.close()

    # Criar todas as tabelas
    Base.metadata.create_all(engine)

    # Criar session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    yield session

    # Cleanup
    session.close()
    engine.dispose()
