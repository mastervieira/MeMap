"""
Lógica de negócio e validação para o formulário guiado.
Implementa o princípio da responsabilidade única, separando a estrutura dos dados da validação.
"""

from typing import Annotated, Any, TypedDict

# Importa componentes centralizados de common
from src.common.utils.validation import (
    validate_positive_number,
)
from src.common.validators.form_validator import (
    BaseFormValidator,
    ValidationResult,
    safe_float_convert,
    safe_int_convert,
)

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
            # Validação de tipos básicos
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

            # Conversão segura de dados
            qtd = safe_int_convert(raw_data["quantidade_recibos"])
            inicio = safe_int_convert(raw_data["recibo_inicio"])
            fim = safe_int_convert(raw_data["recibo_fim"])
            km = safe_float_convert(raw_data["total_km"])

            if None in (qtd, inicio, fim, km):
                return ValidationResult(
                    is_valid=False,
                    error_message="Erro ao converter valores numéricos."
                )

            # Conversão e limpeza de dados
            clean_data: FormPage1Data = {
                "quantidade_recibos": qtd,  # type: ignore
                "recibo_inicio": inicio,  # type: ignore
                "recibo_fim": fim,  # type: ignore
                "zona_primaria": str(raw_data.get("zona_primaria", "")),
                "zona_secundaria": str(raw_data.get("zona_secundaria", "")),
                "total_km": km,  # type: ignore
            }

            # Validação de Regras de Negócio
            if clean_data["recibo_fim"] < clean_data["recibo_inicio"]:
                return ValidationResult(
                    is_valid=False,
                    error_message="O número do recibo final não pode ser menor que o inicial."
                )

            # Validação de consistência: quantidade deve bater com range
            expected_quantity = clean_data["recibo_fim"] - clean_data["recibo_inicio"] + 1
            if clean_data["quantidade_recibos"] != expected_quantity:
                return ValidationResult(
                    is_valid=False,
                    error_message=f"Quantidade ({clean_data['quantidade_recibos']}) não corresponde ao range "
                                f"({expected_quantity} recibos entre {clean_data['recibo_inicio']} e {clean_data['recibo_fim']})."
                )

            return ValidationResult(is_valid=True, data=clean_data)

        except (ValueError, KeyError, TypeError) as e:
            return ValidationResult(
                is_valid=False,
                error_message=f"Erro no processamento dos dados: {str(e)}"
            )
