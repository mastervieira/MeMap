# type: ignore

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QLabel, QSizePolicy, QVBoxLayout, QWidget
import logging

from src.frontend.styles.styles import ColorPalette

AppColors = ColorPalette()


class NotificationManager:
    """Gerenciador de notificações da aplicação."""

    def __init__(self) -> None:
        self.logger: logging.Logger = logging.getLogger(__name__)

    def enviar_sucesso(
            self, mensagem: str,
            dados: dict[str, object] | None = None
            ) -> None:
        """Envia notificação de sucesso."""
        msg_formatada: str = self.formatar_mensagem("SUCESSO", mensagem, dados)
        self.logger.info(msg_formatada)

    def enviar_erro(
            self, mensagem: str,
            dados: dict[str, object] | None = None
            ) -> None:
        """Envia notificação de erro."""
        msg_formatada: str = self.formatar_mensagem("ERRO", mensagem, dados)
        self.logger.error(msg_formatada)

    def enviar_aviso(
            self, mensagem: str,
            dados: dict[str, object] | None = None
            ) -> None:
        """Envia notificação de aviso."""
        msg_formatada: str = self.formatar_mensagem("AVISO", mensagem, dados)
        self.logger.warning(msg_formatada)

    def enviar_debug(
            self, mensagem: str,
            dados: dict[str, object] | None = None
            ) -> None:
        """Envia notificação de debug."""
        msg_formatada: str = self.formatar_mensagem("DEBUG", mensagem, dados)
        self.logger.debug(msg_formatada)

    def formatar_mensagem(
            self, tipo: str,
            mensagem: str,
            dados: dict[str, object] | None = None
            ) -> str:
        """Formata mensagem com tipo e dados adicionais."""
        msg: str = f"[{tipo}] {mensagem}"
        if dados:
            dados_str: str = " | ".join([f"{k}: {v}" for k, v in dados.items()])
            msg += f" | {dados_str}"
        return msg


class NotificationWidget(QWidget):
    closed = Signal()

    def __init__(self, message: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType_Popup)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setWindowFlag(Qt.Tool)
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        layout = QVBoxLayout()
        self.label = QLabel(message)
        self.label.setStyleSheet(f"""
            background-color: {AppColors.SURFACE};
            color: {AppColors.PRIMARY};
            padding: 12px 16px;
            border-radius: 8px;
            font-family: 'Inter', sans-serif;
        """)
        self.label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.adjustSize()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.close)
        self.timer.start(3000)  # Close the notification after 3 seconds

    def closeEvent(self, event: object) -> None:
        self.closed.emit()
        event.accept()
