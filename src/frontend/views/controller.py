# pylint: disable=no-name-in-module
# type: ignore
"""
Controller Mediator para o MeMap Pro.
Gerencia a comunicação entre o Calendário e o Formulário sem acoplamento direto
"""

from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, QObject, Qt
from qasync import asyncSlot

from src.frontend.views.calendar_dashboard import CalendarDashboard

if TYPE_CHECKING:
    from src.frontend.views.main_view import MainView


class CalendarController(QObject):
    """
    Mediador que escuta eventos do Calendário e coordena ações no Formulário.

    A importância do @Slot():
    1. Performance: O Qt otimiza a chamada de slots decorados.
    2. Segurança de Memória: Garante que o C++ do Qt entenda a assinatura
      do método Python.
    3. Introspecção: Permite que o sistema de Meta-Objetos do Qt identifique
    o método corretamente.

    NOTA: GuidedFormWizard (legacy) foi removido. Usar nova arquitetura em
    src/frontend/wizard/ com WizardView, FormViewModel, etc.
    """

    def __init__(
            self, calendar: CalendarDashboard,
            wizard: "QObject | None" = None,
            main_view: "MainView | None" = None
            ) -> None:
        super().__init__()
        self._calendar: CalendarDashboard = calendar
        self._wizard: QObject | None = wizard
        self._main_view: "MainView | None" = main_view

        # Conecta o sinal do calendário ao slot do controller usando QueuedConnection
        # Isso garante que o evento seja processado no próximo ciclo do event loop,
        # evitando bloqueios imediatos e permitindo que a UI respire.
        self._calendar.date_selected.connect(
            self._on_date_selected,
            Qt.ConnectionType.QueuedConnection
        )

    @asyncSlot(QDate)
    async def _on_date_selected(self, date: QDate) -> None:
        """
        Processa a data selecionada de forma assíncrona.
        O uso de @asyncSlot aqui permite coordenar múltiplas tarefas assíncronas.

        NOTA: Código relativo ao wizard foi comentado. A integração com o novo
        wizard (src/frontend/wizard/) será feita em uma fase posterior.
        """
        # Legacy wizard integration commented out (archived code)
        # if self._main_view:
        #     self._main_view._on_page_changed("wizard")
        # if self._wizard:
        #     self._wizard.set_selected_date(date)
        pass
