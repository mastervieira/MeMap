"""Main entry point for MeMap application."""

import asyncio
import os
import sys

# Add project root to PYTHONPATH first
sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..")
    ),
)

# Now import external libraries
from PySide6.QtCore import QCoreApplication
import qasync  # type: ignore[import-not-found]
from PySide6.QtWidgets import QApplication

# Import local modules
from src.common.logging_config import (
    setup_exception_hook,
    setup_logging,
)
from src.frontend.main import main

setup_logging()
setup_exception_hook()

if __name__ == "__main__":
    # Configura o loop de eventos qasync
    try:
        # Cria a aplicação Qt primeiro
        app: QCoreApplication | None = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Cria o loop de eventos
        loop: qasync.QEventLoop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)

        # Executa a aplicação
        with loop:
            exit_code = loop.run_until_complete(main())

        # Encerra a aplicação
        sys.exit(exit_code)

    except Exception as e:
        print(f"Erro ao iniciar a aplicação: {e}")
        sys.exit(1)
