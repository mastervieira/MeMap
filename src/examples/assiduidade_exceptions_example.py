"""Exemplo de uso da hierarquia de exceções para o domínio de Assiduidade.

Este arquivo demonstra como usar as exceções personalizadas para tratar
erros de forma segura e consistente, sem expor detalhes técnicos para
camadas externas da aplicação.
"""

from src.common.execptions.assiduidade import (
    AssiduidadeDomainError,
    MapaAssiduidadeAlreadyExistsError,
    MapaAssiduidadeBusinessRuleError,
    MapaAssiduidadeInvalidStateError,
    MapaAssiduidadeNotFoundError,
    MapaAssiduidadePersistenceError,
    MapaAssiduidadeValidationError,
)
from src.repositories.assiduidade_repository import MapaAssiduidadeRepository


def exemplo_tratamento_excecoes():
    """Exemplo de como tratar exceções no service layer."""

    repository = MapaAssiduidadeRepository(session=None)  # Mock session

    try:
        # Tentativa de criar um mapa com mês inválido
        mapa = repository.criar(mes=13, ano=2024)

    except MapaAssiduidadeValidationError as e:
        # Tratamento de erro de validação
        print("❌ Erro de validação:")
        print(f"   Código: {e.error_code}")
        print(f"   Mensagem: {e.message}")
        print(f"   Detalhes: {e.details}")
        print(f"   Para API: {e.to_dict()}")
        e.log_error("Service - criar mapa")

    try:
        # Tentativa de buscar mapa inexistente
        mapa = repository.buscar_por_id(999)

    except MapaAssiduidadeNotFoundError as e:
        # Tratamento de erro de entidade não encontrada
        print("❌ Mapa não encontrado:")
