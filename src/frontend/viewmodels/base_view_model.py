
from __future__ import annotations

import logging
from abc import ABCMeta, abstractmethod

from PySide6.QtCore import QObject, Signal

logger: logging.Logger = logging.getLogger(__name__)



class ABCQObjectMeta(ABCMeta, type(QObject)):
    """Metaclass que combina ABC e QObject."""
    pass



class BaseViewModel(QObject, metaclass=ABCQObjectMeta):
    """Classe abstrata base para todos os ViewModels."""
    def __init__(self) -> None:
        """Inicializa ViewModel e verifica abstração."""
        # Verificar se algum abstractmethod não foi implementado
        abstract_methods: frozenset[str] = self.__abstractmethods__
        if abstract_methods:
            raise TypeError(
                f"Não é possível instanciar {self.__class__.__name__}. "
                f"Métodos abstractos não implementados: {abstract_methods}"
            )
        super().__init__()

    is_loading_changed = Signal(bool)
    error_occurred = Signal(str)
    success_completed = Signal()

    @abstractmethod
    def on_appear(self) -> None:
        """Chamado quando a View é ativada."""
        pass

    @abstractmethod
    def dispose(self) -> None:
        """Chamado para limpar recursos (sinais, timers, etc)."""
        pass
