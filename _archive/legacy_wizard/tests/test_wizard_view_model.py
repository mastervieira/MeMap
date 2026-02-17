
"""Testes para o WizardViewModel."""

from __future__ import annotations

from src.frontend.viewmodels.wizard_view_model import WizardViewModel


def test_wizard_view_model_instantiation() -> None:
    """WizardViewModel pode ser instanciado."""
    vm = WizardViewModel()
    assert vm is not None
    assert vm._current_page == 0


def test_go_next_navigation() -> None:
    """go_next() avança de página."""
    vm = WizardViewModel()
    pages = []

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.current_page_changed.connect(on_page_changed)
    vm.go_next()

    assert vm._current_page == 1
    assert pages == [1]


def test_go_next_blocks_at_last_page() -> None:
    """go_next() não avança além da última página."""
    vm = WizardViewModel()
    pages = []

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.current_page_changed.connect(on_page_changed)

    # Avançar para a última página
    vm.go_next()
    pages.clear()

    # Tentar avançar novamente (não deve funcionar)
    vm.go_next()
    assert vm._current_page == 1
    assert pages == []


def test_go_back_navigation() -> None:
    """go_back() volta à página anterior."""
    vm = WizardViewModel()
    pages = []

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.current_page_changed.connect(on_page_changed)

    # Avançar primeiro
    vm.go_next()
    pages.clear()

    # Depois voltar
    vm.go_back()
    assert vm._current_page == 0
    assert pages == [0]


def test_go_back_blocks_at_first_page() -> None:
    """go_back() não volta antes da primeira página."""
    vm = WizardViewModel()
    pages = []

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.current_page_changed.connect(on_page_changed)

    # Tentar voltar na primeira página (não deve funcionar)
    vm.go_back()
    assert vm._current_page == 0
    assert pages == []


def test_go_to_page_valid() -> None:
    """go_to_page() navega para página válida."""
    vm = WizardViewModel()
    pages = []

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.current_page_changed.connect(on_page_changed)
    vm.go_to_page(1)

    assert vm._current_page == 1
    assert pages == [1]


def test_go_to_page_invalid() -> None:
    """go_to_page() bloqueia para página inválida."""
    vm = WizardViewModel()
    pages = []

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.current_page_changed.connect(on_page_changed)
    vm.go_to_page(5)

    assert vm._current_page == 0
    assert pages == []

# ======== TESTES DE VALIDAÇÃO HÍBRIDA ========

class StrictValidationViewModel(WizardViewModel):
    """Subclass que exige page_1 completo."""
    def __init__(self, page1_valid: bool = False):
        super().__init__()
        self.page1_complete = page1_valid

    def _validate_current_page(self) -> bool:
        """Validar página 1."""
        if self._current_page == 0:
            return self.page1_complete
        return True


def test_validation_error_signal() -> None:
    """Signal de validação é emitido quando falha."""
    vm = StrictValidationViewModel(page1_valid=False)
    errors = []
    pages = []

    def on_error(msg: str) -> None:
        errors.append(msg)

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.validation_error.connect(on_error)
    vm.current_page_changed.connect(on_page_changed)

    # Tentar avançar sem validação passar
    vm.go_next()

    assert len(errors) == 1
    assert "inválida" in errors[0]
    assert pages == []  # Não avançou


def test_validation_passes() -> None:
    """Avança quando validação passa."""
    vm = StrictValidationViewModel(page1_valid=True)
    errors = []
    pages = []

    def on_error(msg: str) -> None:
        errors.append(msg)

    def on_page_changed(page: int) -> None:
        pages.append(page)

    vm.validation_error.connect(on_error)
    vm.current_page_changed.connect(on_page_changed)

    # Avançar com validação passando
    vm.go_next()

    assert len(errors) == 0  # Sem erros
    assert vm._current_page == 1
    assert pages == [1]


def test_default_validation_always_passes() -> None:
    """WizardViewModel padrão não rejeita nenhuma navegação."""
    vm = WizardViewModel()
    errors = []

    def on_error(msg: str) -> None:
        errors.append(msg)

    vm.validation_error.connect(on_error)

    vm.go_next()
    assert len(errors) == 0
    assert vm._current_page == 1
