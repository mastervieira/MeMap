"""Testes para os ViewModels."""

from __future__ import annotations

import pytest

from src.frontend.viewmodels.base_view_model import BaseViewModel


def test_base_view_model_is_abstract() -> None:
    """BaseViewModel não pode ser instanciada directamente."""
    with pytest.raises(TypeError):
        BaseViewModel()



class MockViewModel(BaseViewModel):
    """ViewModel concreta para testes."""

    def on_appear(self) -> None:
        """Implementação concreta."""
        pass

    def dispose(self) -> None:
        """Implementação concreta."""
        pass


def test_view_model_subclass_works() -> None:
    """Subclasses podem ser instanciadas
    se implementarem abstractmethods."""
    vm = MockViewModel()
    assert vm is not None


def test_signals_emit() -> None:
    """Signals podem ser conectados e emitidos."""
    vm = MockViewModel()
    signal_fired = []

    def on_loading(is_loading: bool) -> None:
        signal_fired.append(is_loading)

    vm.is_loading_changed.connect(on_loading)
    vm.is_loading_changed.emit(True)

    assert signal_fired == [True]
