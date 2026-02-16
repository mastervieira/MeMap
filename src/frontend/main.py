"""
Aplicação principal com integração qasync para suporte total a async/await.
Demonstra como combinar PySide6 com qasync para criar uma aplicação desktop profissional.
"""

import asyncio
import logging
import sys
from typing import Optional

# Importa qasync para suporte a async/await
import qasync
from PySide6.QtCore import Qt

# Importa componentes da aplicação
from PySide6.QtWidgets import QApplication

from src.frontend.views.main_view import MainView
from src.frontend.components.notifications import NotificationManager
from src.frontend.views.notifications import StatusManager



class ApplicationManager:
    """
    Gerenciador principal da aplicação.

    Responsabilidades:
    - Inicializar a aplicação com qasync
    - Gerenciar o ciclo de vida da aplicação
    - Coordenar a integração entre UI e workers assíncronos
    - Gerenciar recursos e limpeza
    """

    def __init__(self):
        self.app: Optional[QApplication] = None
        self.main_view: Optional[MainView] = None
        self.notification_manager: Optional[NotificationManager] = None
        self.status_manager: Optional[StatusManager] = None
        self.current_worker: Optional[asyncio.Task] = None

        # Configuração de logging
        self._setup_logging()

    def _setup_logging(self):
        """Configura o sistema de logging."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('memap_pro.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # Suprimir erros do qasync durante encerramento (esperados e inofensivos)
        qasync_logger = logging.getLogger('qasync')
        qasync_logger.setLevel(logging.CRITICAL)  # Apenas erros críticos, não ERROR

    async def initialize(self):
        """Inicializa a aplicação de forma assíncrona."""
        self.logger.info("Iniciando MeMap Pro...")

        # Usa a aplicação Qt existente ou cria uma nova
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)

        self.app.setApplicationName("MeMap Pro")
        self.app.setApplicationVersion("1.0.0")
        self.app.setOrganizationName("MeMap")
        self.app.setOrganizationDomain("memap.pro")

        # Configurações globais
        self._setup_global_settings()

        # Cria a interface principal
        self.main_view = MainView()
        self.logger.info(f"MainView criada: {self.main_view}")
        self.logger.info(f"MainView isVisible: {self.main_view.isVisible()}")
        self.logger.info(f"MainView geometry antes de showMaximized: {self.main_view.geometry()}")
        self.logger.info(f"MainView screen: {self.main_view.screen()}")

        # Tenta maximizar a janela
        self.main_view.showMaximized()
        self.logger.info("showMaximized() chamado")
        self.logger.info(f"MainView isVisible após showMaximized: {self.main_view.isVisible()}")
        self.logger.info(f"MainView geometry após showMaximized: {self.main_view.geometry()}")
        self.logger.info(f"MainView windowState: {self.main_view.windowState()}")

        # Força o processamento de eventos para aplicar a maximização
        self.app.processEvents()
        self.logger.info(f"MainView geometry após processEvents: {self.main_view.geometry()}")
        self.logger.info(f"MainView screen geometry: {self.main_view.screen().geometry()}")

        # Remove as chamadas de resize que estão causando overflow
        # Apenas deixa o showMaximized() fazer seu trabalho
        self.app.processEvents()
        self.logger.info(f"MainView geometry final: {self.main_view.geometry()}")

        # Ajusta o tamanho da janela para o layout correto
        self.main_view.adjustSize()
        self.app.processEvents()
        self.logger.info(f"MainView geometry após adjustSize: {self.main_view.geometry()}")

        # Inicializa gerenciadores
        self.notification_manager = NotificationManager.instance(self.main_view)
        self.status_manager = StatusManager(self.main_view.navbar)

        # Conecta sinais
        self._connect_signals()

        self.logger.info("MeMap Pro inicializado com sucesso!")

        # Cria um Future que será resolvido quando a aplicação fechar
        self._exit_future = asyncio.Future()

        # Conecta o sinal de encerramento do Qt ao Future
        # Usa set_result apenas se o Future ainda não estiver resolvido
        def on_quit():
            if not self._exit_future.done():
                self._exit_future.set_result(0)

        self.app.aboutToQuit.connect(on_quit)

        # Aguarda até a aplicação ser fechada
        try:
            exit_code = await self._exit_future
        except asyncio.CancelledError:
            # Se a tarefa foi cancelada durante o shutdown, retorna 0
            exit_code = 0

        return exit_code

    def _setup_global_settings(self) -> None:
        """Configurações globais da aplicação."""
        if self.app:
            # Estilo
            self.app.setStyle("Fusion")

            # Fonte padrão
            font = self.app.font()
            font.setFamily("Segoe UI")
            font.setPointSize(10)
            self.app.setFont(font)

            # Cursor padrão (removido - causa warnings no Qt)
            # self.app.setOverrideCursor(Qt.ArrowCursor)

    def _connect_signals(self) -> None:
        """Conecta sinais globais da aplicação."""
        if self.main_view and self.notification_manager:
            # Conecta sinais de workers para notificações
            self._connect_worker_signals()

            # Conecta sinais de UI para status
            self._connect_ui_signals()

    def _connect_worker_signals(self) -> None:
        """Conecta sinais de workers para notificações."""
        if self.main_view:
            # Conecta sinais de páginas específicas
            # Nota: Como removemos as funcionalidades de crypto, cálculos e arquivos,
            # vamos manter apenas a conexão de sinais básicos
            pass

    def _connect_ui_signals(self) -> None:
        """Conecta sinais de UI para status."""
        if self.main_view:
            # Atualiza status quando mudar de página
            self.main_view.sidebar.page_changed.connect(self._on_page_changed)

    def _on_page_changed(self, page_name: str) -> None:
        """Callback quando a página é alterada."""
        titles: dict[str, str] = {
            "dashboard": "Dashboard",
            "recibos": "Recibos",
            "calendar": "Calendário",
            "settings": "Configurações"
        }
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_page_title(titles.get(page_name, page_name))


    def cleanup(self) -> None:
        """Limpa recursos da aplicação."""
        self.logger.info("Limpando recursos...")

        # Para workers ativos
        if self.main_view and hasattr(self.main_view, 'current_worker') and self.main_view.current_worker:
            self.main_view.current_worker.stop()

        # Limpa notificações
        if self.notification_manager:
            self.notification_manager.clear_all()

        # Fecha a aplicação
        if self.app:
            self.app.quit()

        self.logger.info("Recursos limpos com sucesso!")


async def shutdown(loop, signal=None):
    """Cancela todas as tarefas pendentes de forma limpa."""
    if signal:
        logging.info(f"Recebido sinal de encerramento {signal.name}...")

    logging.info("A encerrar tarefas pendentes...")
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

    if tasks:
        for task in tasks:
            task.cancel()

        logging.info(f"A cancelar {len(tasks)} tarefas pendentes...")
        await asyncio.gather(*tasks, return_exceptions=True)

    logging.info("Todas as tarefas canceladas com sucesso.")


async def main():
    """Função principal assíncrona."""
    # Cria o gerenciador da aplicação
    app_manager = ApplicationManager()

    try:
        # Inicializa e executa a aplicação
        exit_code = await app_manager.initialize()
        return exit_code
    except KeyboardInterrupt:
        print("\nAplicação encerrada pelo usuário.")
        return 0
    except Exception as e:
        print(f"Erro crítico: {e}")
        return 1
    finally:
        # Limpa recursos
        app_manager.cleanup()


if __name__ == "__main__":
    # Configura o loop de eventos qasync
    try:
        # Cria a aplicação Qt primeiro
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)

        # Cria o loop de eventos
        loop = qasync.QEventLoop(app)
        asyncio.set_event_loop(loop)

        # Executa a aplicação
        exit_code = 0
        try:
            exit_code = loop.run_until_complete(main())
        except KeyboardInterrupt:
            print("\nAplicação interrompida pelo utilizador.")
        except Exception as e:
            # Silencia erros comuns do qasync no encerramento
            error_str = str(e)
            if "Event loop stopped before Future completed" not in error_str and \
               "Event loop is closed" not in error_str and \
               not isinstance(e, asyncio.CancelledError):
                print(f"Erro durante execução: {e}")
                import traceback
                traceback.print_exc()
        finally:
            # Garante que todas as tarefas são canceladas antes de fechar o loop
            try:
                loop.run_until_complete(shutdown(loop))
            except Exception:
                pass  # Silencia erros durante shutdown

            # Fecha o loop de forma segura
            try:
                loop.close()
            except Exception:
                pass  # Silencia erros ao fechar loop

        # Encerra a aplicação
        sys.exit(exit_code)

    except Exception as e:
        # Último recurso para erros não capturados
        error_str = str(e)
        if "Event loop stopped before Future completed" not in error_str and \
           "Event loop is closed" not in error_str and \
           not isinstance(e, asyncio.CancelledError):
            print(f"Erro crítico ao iniciar: {e}")
        sys.exit(0)
