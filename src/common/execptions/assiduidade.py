"""Exceções personalizadas para o domínio de Assiduidade.

Esta camada de exceções garante que nenhum detalhe técnico seja exposto
para camadas externas da aplicação, mantendo a segurança e consistência.
"""

import logging
from typing import Any

logger: logging.Logger = logging.getLogger(__name__)


class AssiduidadeDomainError(Exception):
    """Exceção base para erros do domínio de Assiduidade.

    Esta exceção NUNCA deve expor detalhes técnicos para o cliente.
    Sempre use mensagens amigáveis e genéricas.
    """

    def __init__(
        self,
        message: str,
        error_code: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        self.message: str = message
        self.error_code: str = error_code or self.__class__.__name__
        self.details: dict[str, Any] = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict[str, Any]:
        """Converte a exceção para um dicionário seguro para serialização."""
        return {
            "error": self.error_code,
            "message": self.message,
            "details": self.details,
        }

    def log_error(self, context: str = "") -> None:
        """Registra o erro nos logs com detalhes técnicos."""
        logger.error(
            f"{context} - {self.error_code}: {self.message}",
            extra={
                "error_code": self.error_code,
                "details": self.details,
                "class": self.__class__.__name__,
            },
        )


# ===== VALIDAÇÃO DE DADOS =====
class MapaAssiduidadeValidationError(AssiduidadeDomainError):
    """Validação de dados do mapa falhou."""

    def __init__(self, field: str, value: Any, reason: str) -> None:
        super().__init__(
            message=f"Valor inválido para campo '{field}': {reason}",
            error_code="VALIDACAO_MAPA_ASSIDUIDADE",
            details={"field": field, "value": value, "reason": reason},
        )


# ===== REGRAS DE NEGÓCIO =====
class MapaAssiduidadeBusinessRuleError(AssiduidadeDomainError):
    """Regra de negócio do mapa de assiduidade violada."""

    def __init__(self, rule: str, details: dict[str, Any] | None = None):
        super().__init__(
            message=f"Regra de negócio violada: {rule}",
            error_code="REGRA_NEGOCIO_ASSIDUIDADE",
            details=details or {"rule": rule}
        )


class MapaAssiduidadeInvalidStateError(AssiduidadeDomainError):
    """Operação inválida para o estado atual do mapa."""

    def __init__(self, mapa_id: int, current_state: str, operation: str):
        super().__init__(
            message=f"Operação '{operation}' não permitida para mapa no estado '{current_state}'.",
            error_code="ESTADO_MAPA_INVALIDO",
            details={
                "mapa_id": mapa_id,
                "current_state": current_state,
                "operation": operation,
            },
        )


class MapaAssiduidadeAlreadyExistsError(AssiduidadeDomainError):
    """Mapa de assiduidade já existe para o período."""

    def __init__(self, mes: int, ano: int) -> None:
        super().__init__(
            message=f"Já existe um mapa de assiduidade para o período {mes}/{ano}.",
            error_code="MAPA_ASSIDUIDADE_JA_EXISTE",
            details={"mes": mes, "ano": ano},
        )


# ===== PERSISTÊNCIA =====
class MapaAssiduidadePersistenceError(AssiduidadeDomainError):
    """Erro ao persistir dados do mapa."""

    def __init__(self, operation: str, original_error: Exception = None):
        super().__init__(
            message=f"Erro ao {operation} mapa de assiduidade.",
            error_code="ERRO_PERSISTENCIA_ASSIDUIDADE",
            details={
                "operation": operation,
                "original_error": (
                    str(original_error) if original_error else None
                ),
            },
        )


class MapaAssiduidadeNotFoundError(AssiduidadeDomainError):
    """Mapa de Assiduidade não encontrado."""

    def __init__(self, mapa_id: int) -> None:
        super().__init__(
            message=f"Mapa de Assiduidade com ID {mapa_id} não encontrado.",
            error_code="MAPA_ASSIDUIDADE_NAO_ENCONTRADO",
            details={"mapa_id": mapa_id},
        )


# ===== AUTORIZAÇÃO/PERMISSÕES =====
class MapaAssiduidadePermissionError(AssiduidadeDomainError):
    """Usuário não tem permissão para operar no mapa."""

    def __init__(self, user_id: int, operation: str, mapa_id: int = None) -> None: # type: ignore
        super().__init__(
            message=f"Usuário {user_id} não tem permissão para {operation}.",
            error_code="PERMISSAO_NEGADA_ASSIDUIDADE",
            details={
                "user_id": user_id,
                "operation": operation,
                "mapa_id": mapa_id,
            },
        )


# ===== ERROS INESPERADOS =====
class MapaAssiduidadeUnexpectedError(AssiduidadeDomainError):
    """Erro inesperado no domínio de assiduidade."""

    def __init__(self, operation: str, original_error: Exception) -> None:
        super().__init__(
            message=f"Ocorreu um erro inesperado ao {operation}.",
            error_code="ERRO_INESPERADO_ASSIDUIDADE",
            details={
                "operation": operation,
                "original_error": str(original_error),
            },
        )
