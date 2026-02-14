"""Gerenciador de sessões SQLAlchemy para a aplicação MeMap.

Implementa Singleton pattern para garantir única instância do engine e session factory.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

if TYPE_CHECKING:
    from sqlalchemy.engine import Engine

logger: logging.Logger = logging.getLogger(__name__)


class SessionManager:
    """Gerenciador singleton de sessões SQLAlchemy.

    Responsabilidades:
    - Criar e gerenciar engine SQLAlchemy
    - Fornecer session factory
    - Garantir única instância (Singleton)
    """

    _instance: SessionManager | None = None
    _engine: Engine | None = None
    _session_factory: sessionmaker[Session] | None = None

    @classmethod
    def get_instance(cls) -> SessionManager:
        """Retorna instância singleton do SessionManager.

        Returns:
            Instância única do SessionManager
        """
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self, db_path: str | None = None) -> None:
        """Inicializa o SessionManager.

        Args:
            db_path: Caminho do banco de dados SQLite.
                    Se None, usa "memap.db" no diretório do projeto.

        Note:
            Não chamar diretamente. Usar get_instance() para obter singleton.
        """
        if SessionManager._engine is not None:
            # Já inicializado
            return

        # Definir caminho do BD
        if db_path is None:
            # Usar diretório do projeto
            project_root = Path(__file__).parent.parent.parent
            db_path = str(project_root / "memap.db")

        # Criar engine SQLite
        SessionManager._engine = create_engine(
            f"sqlite:///{db_path}",
            connect_args={"check_same_thread": False},  # Necessário para SQLite
            echo=False,  # Set True para debug SQL
            pool_pre_ping=True,  # Verifica conexão antes de usar
        )

        # Criar session factory
        SessionManager._session_factory = sessionmaker(
            bind=SessionManager._engine,
            expire_on_commit=False,  # Mantém objetos utilizáveis após commit
        )

        # Criar tabelas se não existirem
        from src.db.models.base_mixin import Base
        Base.metadata.create_all(SessionManager._engine)
        logger.debug("Tabelas criadas/verificadas no BD")

        logger.info(f"SessionManager inicializado com BD: {db_path}")

    def get_session(self) -> Session:
        """Cria e retorna nova sessão SQLAlchemy.

        Returns:
            Nova sessão para interagir com BD

        Example:
            ```python
            session_manager = SessionManager.get_instance()
            session = session_manager.get_session()

            try:
                # Usar session
                user = session.query(User).first()
            finally:
                session.close()
            ```
        """
        if SessionManager._session_factory is None:
            raise RuntimeError(
                "SessionManager não inicializado. Chamar get_instance() primeiro."
            )

        return SessionManager._session_factory()

    def get_engine(self) -> Engine:
        """Retorna engine SQLAlchemy.

        Returns:
            Engine do SQLAlchemy

        Raises:
            RuntimeError: Se SessionManager não foi inicializado
        """
        if SessionManager._engine is None:
            raise RuntimeError(
                "SessionManager não inicializado. Chamar get_instance() primeiro."
            )

        return SessionManager._engine

    @classmethod
    def reset(cls) -> None:
        """Reseta singleton (útil para testes).

        Warning:
            Apenas para testes! Não usar em produção.
        """
        if cls._engine:
            cls._engine.dispose()

        cls._instance = None
        cls._engine = None
        cls._session_factory = None

        logger.debug("SessionManager resetado")
