"""
Lógica de negócio e validação para o formulário guiado.
Implementa o princípio da responsabilidade única, separando a estrutura dos dados da validação.
"""

from typing import Annotated, TypedDict, TypeVar, Generic, Any, Final
from dataclasses import dataclass, field
from enum import Enum

# --- Simulação de Dependências Internas (Módulo 'common') ---
# Em um cenário real, estes seriam importados de src.common
def validate_positive_number(value: Any) -> bool:
    """Simula um validador genérico do módulo common."""
    try:
        return float(str(value).replace(",", ".")) >= 0
    except ValueError:
        return False

class BaseFormValidator:
    """Classe base simulada do módulo common."""
    def __init__(self):
        self.errors: list[str] = []

# --- Definições de Tipos e Enums ---

class ZonaTrabalho(Enum):
    """Zonas de trabalho disponíveis para seleção."""
    NORTE = "Norte"
    SUL = "Sul"
    CENTRO = "Centro"
    LISBOA = "Lisboa"
    ALGARVE = "Algarve"
    ILHAS = "Ilhas"

# Uso de Annotated para metadados de validação (Python 3.10+)
PositiveInt = Annotated[int, "Deve ser >= 0"]
PositiveFloat = Annotated[float, "Deve ser >= 0.0"]

class FormPage1Data(TypedDict):
    """Estrutura de dados tipada para a primeira página do formulário."""
    quantidade_recibos: PositiveInt
    recibo_inicio: PositiveInt
    recibo_fim: PositiveInt
    zona_primaria: str
    zona_secundaria: str
    total_km: PositiveFloat

@dataclass(frozen=True)
class ValidationResult:
    """Resultado imutável de uma operação de validação."""
    is_valid: bool
    data: FormPage1Data | None = None
    error_message: str | None = None

# --- Lógica de Validação (Responsabilidade Única) ---

class WizardValidator(BaseFormValidator):
    """
    Responsável exclusivamente por validar os dados de entrada do Wizard.
    Mantém a lógica de negócio separada da interface gráfica.
    """

    def validate_page_1(self, raw_data: dict[str, Any]) -> ValidationResult:
        """
        Executa a validação completa dos campos da Página 1.
        Retorna um objeto ValidationResult com os dados limpos ou erro.
        """
        try:
            # Validação de tipos básicos usando os simuladores do 'common'
            if not all([
                validate_positive_number(raw_data.get("quantidade_recibos")),
                validate_positive_number(raw_data.get("recibo_inicio")),
                validate_positive_number(raw_data.get("recibo_fim")),
                validate_positive_number(raw_data.get("total_km"))
            ]):
                return ValidationResult(
                    is_valid=False,
                    error_message="Certifique-se de que todos os campos numéricos são positivos."
                )

            # Conversão e limpeza de dados
            clean_data: FormPage1Data = {
                "quantidade_recibos": int(raw_data["quantidade_recibos"]),
                "recibo_inicio": int(raw_data["recibo_inicio"]),
                "recibo_fim": int(raw_data["recibo_fim"]),
                "zona_primaria": str(raw_data.get("zona_primaria", "")),
                "zona_secundaria": str(raw_data.get("zona_secundaria", "")),
                "total_km": float(str(raw_data["total_km"]).replace(",", ".")),
            }

            # Validação de Regras de Negócio
            if clean_data["recibo_fim"] < clean_data["recibo_inicio"]:
                return ValidationResult(
                    is_valid=False,
                    error_message="O número do recibo final não pode ser menor que o inicial."
                )

            return ValidationResult(is_valid=True, data=clean_data)

        except (ValueError, KeyError, TypeError) as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Erro no processamento dos dados: {str(e)}"
            )
