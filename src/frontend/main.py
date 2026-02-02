"""
Aplicação principal com integração qasync para suporte total a async/await.
Demonstra como combinar PySide6 com qasync para criar uma aplicação desktop profissional.
"""

import sys
import asyncio
import logging
from typing import Optional

# Importa qasync para suporte a async/await
import qasync

# Importa componentes da aplicação
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtGui import QIcon

from src.frontend.views.main_view import MainView
from src.frontend.views.notifications import NotificationManager, StatusManager
# from src.frontend.workers.async_worker import CryptoWorker, HeavyCalculationWorker, FileProcessorWorker


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
        self.logger.info(f"showMaximized() chamado")
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
        self.notification_manager = NotificationManager(self.main_view)
        self.status_manager = StatusManager(self.main_view.navbar)

        # Conecta sinais
        self._connect_signals()

        # Exibe notificação de boas-vindas
        self.notification_manager.show_info(
            "Bem-vindo ao MeMap Pro! Sistema PySide6 + qasync iniciado com sucesso.",
            duration=5000
        )

        self.logger.info("MeMap Pro inicializado com sucesso!")

        # Inicia loop principal
        return await self._main_loop()

    def _setup_global_settings(self):
        """Configurações globais da aplicação."""
        if self.app:
            # Estilo
            self.app.setStyle("Fusion")

            # Fonte padrão
            font = self.app.font()
            font.setFamily("Segoe UI")
            font.setPointSize(10)
            self.app.setFont(font)

            # Cursor padrão
            self.app.setOverrideCursor(Qt.ArrowCursor)

    def _connect_signals(self):
        """Conecta sinais globais da aplicação."""
        if self.main_view and self.notification_manager:
            # Conecta sinais de workers para notificações
            self._connect_worker_signals()

            # Conecta sinais de UI para status
            self._connect_ui_signals()

    def _connect_worker_signals(self):
        """Conecta sinais de workers para notificações."""
        if self.main_view:
            # Conecta sinais de páginas específicas
            # Nota: Como removemos as funcionalidades de crypto, cálculos e arquivos,
            # vamos manter apenas a conexão de sinais básicos
            pass

    def _connect_ui_signals(self):
        """Conecta sinais de UI para status."""
        if self.main_view:
            # Atualiza status quando mudar de página
            self.main_view.sidebar.page_changed.connect(self._on_page_changed)

    def _on_crypto_started(self):
        """Callback quando worker de criptomoedas inicia."""
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_status("Carregando dados de criptomoedas...")
        if self.notification_manager:
            self.notification_manager.show_info("Iniciando carregamento de criptomoedas...")

    def _on_crypto_stopped(self):
        """Callback quando worker de criptomoedas para."""
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_status("Carregamento de criptomoedas interrompido.")
        if self.notification_manager:
            self.notification_manager.show_warning("Carregamento de criptomoedas interrompido pelo usuário.")

    def _on_calculation_started(self, calc_type: str):
        """Callback quando worker de cálculo inicia."""
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_status(f"Iniciando cálculo {calc_type}...")
        if self.notification_manager:
            self.notification_manager.show_info(f"Iniciando cálculo {calc_type}...")

    def _on_calculation_stopped(self):
        """Callback quando worker de cálculo para."""
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_status("Cálculo interrompido.")
        if self.notification_manager:
            self.notification_manager.show_warning("Cálculo interrompido pelo usuário.")

    def _on_file_started(self, operation: str):
        """Callback quando worker de arquivo inicia."""
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_status(f"Iniciando operação {operation}...")
        if self.notification_manager:
            self.notification_manager.show_info(f"Iniciando operação {operation}...")

    def _on_file_stopped(self):
        """Callback quando worker de arquivo para."""
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_status("Operação de arquivo interrompida.")
        if self.notification_manager:
            self.notification_manager.show_warning("Operação de arquivo interrompida pelo usuário.")

    def _on_page_changed(self, page_name: str):
        """Callback quando a página é alterada."""
        titles = {
            "dashboard": "Dashboard",
            "crypto": "Criptomoedas",
            "calculations": "Cálculos",
            "files": "Arquivos",
            "settings": "Configurações"
        }
        if self.main_view and hasattr(self.main_view, 'navbar'):
            self.main_view.navbar.set_page_title(titles.get(page_name, page_name))

    async def _main_loop(self):
        """Loop principal da aplicação."""
        try:
            # Mantém a aplicação rodando
            while True:
                # Atualiza status periódico
                await self._update_status_periodic()

                # Pequena pausa para não consumir 100% da CPU
                await asyncio.sleep(1)

        except asyncio.CancelledError:
            self.logger.info("Aplicação encerrada pelo usuário.")
            return 0
        except Exception as e:
            self.logger.error(f"Erro na aplicação: {e}")
            self.notification_manager.show_error(f"Erro crítico: {str(e)}")
            return 1

    async def _update_status_periodic(self):
        """Atualiza status periodicamente."""
        # Verifica se há workers ativos
        if self.main_view and hasattr(self.main_view, 'current_worker') and self.main_view.current_worker:
            if self.main_view.current_worker.is_running():
                if self.status_manager:
                    self.status_manager.set_status("Processando tarefa em segundo plano...")
                return

        # Status padrão
        if self.status_manager:
            self.status_manager.set_status("Pronto")

    def cleanup(self):
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

    for task in tasks:
        task.cancel()

    logging.info(f"A cancelar {len(tasks)} tarefas pendentes...")
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


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
        try:
            exit_code = loop.run_until_complete(main())
        finally:
            # Garante que todas as tarefas são canceladas antes de fechar o loop
            loop.run_until_complete(shutdown(loop))
            loop.close()

        # Encerra a aplicação
        sys.exit(exit_code)

    except Exception as e:
        # Silencia o erro comum do qasync no encerramento
        if "Event loop stopped before Future completed" in str(e):
            sys.exit(0)

        if not isinstance(e, asyncio.CancelledError):
            print(f"Erro ao iniciar loop de eventos: {e}")
        sys.exit(0)
