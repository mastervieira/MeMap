from enum import Enum

# =============================================================================
# ENUMS
# =============================================================================


class UserRole(str, Enum):
    """Papel do utilizador no sistema."""

    ADMIN = "ADMIN"  # Acesso total, BD Central, pode aprovar valores
    TECNICO = "TECNICO"  # Acesso normal, BD Distribuição


class ModoBD(str, Enum):
    """Modo de operação da base de dados."""

    CENTRAL = "CENTRAL"  # BD principal (Bruno) - detecta, aprova, exporta
    DISTRIBUICAO = "DISTRIBUICAO"  # BD técnicos - só importa updates


class EstadoDocumento(str, Enum):
    """Estado do documento/mapa."""

    RASCUNHO = "rascunho"  # Em edição no wizard
    ABERTO = "aberto"  # Finalizado mas editável
    FECHADO = "fechado"  # Fechado, read-only


class TipoDiaAssiduidade(str, Enum):
    """Tipo de dia no Mapa de Assiduidade."""

    TRABALHO = "trabalho"
    SABADO = "sabado"
    DOMINGO = "domingo"
    FERIADO = "feriado"
    AUSENCIA = "ausencia"
    FERIAS = "ferias"

    
class ZonaTrabalho(Enum):
    """Zonas de trabalho disponíveis para seleção."""
    SETUBAL = "Setúbal"
    SANTAREM = "Santarém"
    EVORA = "Évora"
