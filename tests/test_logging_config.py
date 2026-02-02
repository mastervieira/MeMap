# tests/test_logging_config.py
import logging
import pytest
from pathlib import Path
from src.common.logging_config import setup_logging, setup_exception_hook


def test_setup_logging_creates_file(tmp_path):
    """Test that logging creates log file."""
    log_file = tmp_path / "test.log"

    setup_logging(log_file=str(log_file))

    # Log uma mensagem
    logger = logging.getLogger(__name__)
    logger.info("Test message")

    # Verificar que ficheiro foi criado
    assert log_file.exists()

    # Verificar conteúdo
    content = log_file.read_text()
    assert "Test message" in content


def test_setup_logging_validates_max_bytes():
    """Test that invalid max_bytes raises error."""
    with pytest.raises(ValueError):
        setup_logging(max_bytes=-1)  # ❌ Inválido


def test_setup_logging_validates_backup_count():
    """Test that invalid backup_count raises error."""
    with pytest.raises(ValueError):
        setup_logging(backup_count=0)  # ❌ Inválido
