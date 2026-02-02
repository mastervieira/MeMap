
# Magic bytes para ficheiros Office Open XML (xlsx)
XLSX_MAGIC = b"PK\x03\x04"

# Magic bytes para ficheiros Office antigos (xls)
XLS_MAGIC = b"\xd0\xcf\x11\xe0"

# Extensões permitidas
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}

# Fórmulas perigosas
DANGEROUS_FORMULAS = {
    "WEBSERVICE",
    "FILTERXML",
    "CALL",
    "REGISTER.ID",
    "EXEC",
    "SHELL",
    "HYPERLINK",  # Pode ser usado para phishing
}

# Limites
MAX_FILE_SIZE_MB = 50  # 50 MB
MAX_ROWS = 100_000
MAX_COLS = 100
MAX_SHEETS = 20
