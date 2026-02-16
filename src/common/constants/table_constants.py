"""
Constantes para tabelas do projeto MeMap Pro.
Define estrutura e configuração de tabelas.
"""

from typing import Final

# Colunas da tabela de recibos
RECIBOS_TABLE_COLUMNS: Final[list[str]] = [
    "Recibo",
    "Setúbal",
    "Santarém",
    "Évora",
    "Nº IP's",
    "Div.",
    "Partilhado",
    "Km",
    "Ações"  # NOVA: Coluna para ações (eliminar linha)
]

# Índices das colunas (para acesso por nome)
class ReciboColumn:
    """Índices das colunas da tabela de recibos."""
    RECIBO: Final[int] = 0
    SETUBAL: Final[int] = 1
    SANTAREM: Final[int] = 2
    EVORA: Final[int] = 3
    NUM_IPS: Final[int] = 4
    DIV: Final[int] = 5
    PARTILHADO: Final[int] = 6
    KM: Final[int] = 7
    ACOES: Final[int] = 8  # NOVA: Coluna de ações

# Larguras padrão das colunas (em pixels)
COLUMN_WIDTHS: Final[dict[str, int]] = {
    "Recibo": 120,
    "Setúbal": 180,
    "Santarém": 180,
    "Évora": 180,
    "Nº IP's": 120,
    "Div.": 180,
    "Partilhado": 350,  # Aumentado para acomodar widget expandido
    "Km": 110,  # Reduzido de 120 para 110 (-10px)
    "Ações": 40  # NOVA: Mini-coluna para ícone de eliminar
}

# Configuração de células editáveis
EDITABLE_COLUMNS: Final[set[int]] = {
    ReciboColumn.SETUBAL,
    ReciboColumn.SANTAREM,
    ReciboColumn.EVORA,
    ReciboColumn.NUM_IPS,
    ReciboColumn.DIV,
    ReciboColumn.PARTILHADO,
    ReciboColumn.KM
}

# Colunas numéricas (para validação)
NUMERIC_COLUMNS: Final[set[int]] = {
    ReciboColumn.SETUBAL,
    ReciboColumn.SANTAREM,
    ReciboColumn.EVORA,
    ReciboColumn.NUM_IPS,
    ReciboColumn.DIV,
    ReciboColumn.KM
}

# Placeholder para células vazias
DEFAULT_CELL_VALUE: Final[str] = "0"
# others
TOTAL_ROW_LABEL: Final[str] = "TOTAIS"
ROW_HEIGHT: Final[int] = 50

# ==================== WIZARD CONSTANTS (Phase 2) ====================

# Nomes de dias da semana em português
DAY_NAMES: Final[dict[int, str]] = {
    1: "Segunda",
    2: "Terça",
    3: "Quarta",
    4: "Quinta",
    5: "Sexta",
    6: "Sábado",
    7: "Domingo",
}

# Colunas numéricas da tabela (nomes de colunas)
NUMERIC_COLUMN_NAMES: Final[list[str]] = [
    "Setúbal",
    "Santarém",
    "Évora",
    "Nº IP's",
    "Km",
]

# Colunas de distritos (para cálculo de totais)
DISTRICT_COLUMNS: Final[list[str]] = [
    "Setúbal",
    "Santarém",
    "Évora",
]

# Estrutura esperada de wizard_data (documentação)
WIZARD_DATA_STRUCTURE: Final[dict[str, object]] = {
    "dias": {}  # {"13": {"form": {...}, "table": [...]}, "14": {...}}
}
