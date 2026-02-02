"""
Constantes de caminhos (Paths) do projeto MeMap Pro.
Define todos os caminhos importantes da aplicação.
"""

from pathlib import Path


class Paths:
    """Classe com constantes de caminhos do projeto."""

    # Diretório raiz do projeto
    PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

    # Diretórios principais
    SRC_DIR = PROJECT_ROOT / "src"
    FRONTEND_DIR = SRC_DIR / "frontend"
    BACKEND_DIR = SRC_DIR / "backend"
    COMMON_DIR = SRC_DIR / "common"
    DATABASE_DIR = SRC_DIR / "database"
    DB_DIR = SRC_DIR / "db"

    # Diretórios de frontend
    STYLES_DIR = FRONTEND_DIR / "styles"
    VIEWS_DIR = FRONTEND_DIR / "views"
    WORKERS_DIR = FRONTEND_DIR / "workers"

    # Arquivos de estilos
    STYLES_FILE = STYLES_DIR / "styles.py"
    STYLE_MANAGER_PATH = "src.frontend.styles.styles"

    # Diretórios de dados
    LOGS_DIR = PROJECT_ROOT / "logs"
    DATA_DIR = PROJECT_ROOT / "data"
    CACHE_DIR = PROJECT_ROOT / ".cache"

    # Arquivos de configuração
    CONFIG_DIR = PROJECT_ROOT / "config"
    ENV_FILE = PROJECT_ROOT / ".env"

    @classmethod
    def ensure_directories(cls):
        """Cria os diretórios necessários se não existirem."""
        for directory in [cls.LOGS_DIR, cls.DATA_DIR, cls.CACHE_DIR, cls.CONFIG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_log_file(cls, name: str = "memap_pro") -> Path:
        """Retorna o caminho do arquivo de log."""
        cls.ensure_directories()
        return cls.LOGS_DIR / f"{name}.log"

    @classmethod
    def get_data_file(cls, name: str) -> Path:
        """Retorna o caminho do arquivo de dados."""
        cls.ensure_directories()
        return cls.DATA_DIR / name

    @classmethod
    def get_cache_file(cls, name: str) -> Path:
        """Retorna o caminho do arquivo de cache."""
        cls.ensure_directories()
        return cls.CACHE_DIR / name
