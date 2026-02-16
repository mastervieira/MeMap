"""
Sistema de notificações (Toast) para a aplicação.
Implementa mensagens de status que aparecem temporariamente sem interromper o fluxo.
"""

from PySide6.QtCore import Qt, QTimer, QEasingCurve, QPropertyAnimation, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QLinearGradient
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QPushButton

from src.common.themes import ThemeManager


class ToastNotification(QWidget):
    """
    Componente de notificação Toast que aparece temporariamente.

    Características:
    - Animação suave de entrada e saída
    - Diferentes tipos de mensagens (info, sucesso, erro, aviso)
    - Auto-desaparecimento após tempo configurável
    - Não interrompe o fluxo da aplicação
    """

    # Sinais
    dismissed = Signal()

    def __init__(self, parent=None) -> None:
        super().__init__(parent)

        # Theme manager
        self.theme_manager = ThemeManager()

        # Configurações iniciais
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedHeight(60)

        # Layout principal
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(16, 12, 16, 12)
        self.main_layout.setSpacing(12)

        # Ícone
        self.icon_label = QLabel()
        self.icon_label.setFixedWidth(24)
        self.icon_label.setAlignment(Qt.AlignCenter)

        # Texto da mensagem
        self.message_label = QLabel()
        # Cor será definida dinamicamente ao mostrar a mensagem

        # Botão de fechar
        self.close_button = QLabel("✕")
        self.close_button.setFixedWidth(20)
        self.close_button.setAlignment(Qt.AlignCenter)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        # Cor será definida dinamicamente ao mostrar a mensagem
        self.close_button.mousePressEvent = self._on_close_clicked

        # Adiciona widgets ao layout
        self.main_layout.addWidget(self.icon_label)
        self.main_layout.addWidget(self.message_label, 1)  # Expande
        self.main_layout.addWidget(self.close_button)

        # Animações
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuad)

        # Timer de auto-desaparecimento
        self.auto_hide_timer = QTimer(self)
        self.auto_hide_timer.setSingleShot(True)
        self.auto_hide_timer.timeout.connect(self.hide_with_animation)

        # Estado
        self._is_visible = False
        self._message_type = "info"

    def paintEvent(self, event):
        """Desenha o fundo arredondado do toast."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Cria o caminho arredondado
        path = QPainterPath()
        path.addRoundedRect(self.rect(), 12, 12)

        # Obtém a paleta de cores do tema atual
        palette = self.theme_manager.current_palette

        # Define a cor de fundo baseado no tipo de mensagem
        colors = {
            "info": QColor(palette.background_tertiary),
            "success": QColor(palette.success_pressed),
            "error": QColor(palette.error_pressed),
            "warning": QColor(palette.warning_pressed)
        }

        color = colors.get(self._message_type, QColor(palette.background_tertiary))

        # Cria gradiente
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, color.lighter(120))
        gradient.setColorAt(1, color.darker(110))

        painter.fillPath(path, gradient)

        # Borda sutil usando cor do tema
        border_color = QColor(palette.border)
        border_color.setAlpha(100)
        painter.setPen(border_color)
        painter.drawPath(path)

    def show_message(self, message: str, message_type: str = "info", duration: int = 3000):
        """
        Exibe uma mensagem de toast.

        Args:
            message: Texto da mensagem
            message_type: Tipo da mensagem ("info", "success", "error", "warning")
            duration: Duração em milissegundos (0 = permanente até fechar manualmente)
        """
        self._message_type = message_type
        self.message_label.setText(message)

        # Define cores baseadas no tema
        palette = self.theme_manager.current_palette

        # Define estilo dos textos
        self.message_label.setStyleSheet(f"""
            QLabel {{
                font-size: 14px;
                font-weight: 500;
                color: {palette.text_primary};
            }}
        """)

        self.close_button.setStyleSheet(f"""
            QLabel {{
                font-size: 16px;
                color: {palette.text_secondary};
                font-weight: bold;
            }}
        """)

        # Define ícone baseado no tipo
        icons = {
            "info": "ℹ️",
            "success": "✅",
            "error": "❌",
            "warning": "⚠️"
        }
        self.icon_label.setText(icons.get(message_type, "ℹ️"))

        # Define posição (normalmente no canto superior direito)
        if self.parent():
            parent_rect = self.parent().rect()
            self.move(parent_rect.width() - self.width() - 20, 20)
        else:
            # Se não tem parent, posiciona no centro da tela
            screen = self.screen().availableGeometry()
            self.move(screen.width() - self.width() - 20, 20)

        # Mostra com animação
        self.show()
        self._is_visible = True
        self.setWindowOpacity(0)

        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()

        # Configura timer de auto-desaparecimento
        if duration > 0:
            self.auto_hide_timer.start(duration)

    def hide_with_animation(self):
        """Esconde o toast com animação."""
        if not self._is_visible:
            return

        self._is_visible = False
        self.auto_hide_timer.stop()

        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self._on_animation_finished)
        self.animation.start()

    def _on_animation_finished(self):
        """Callback quando a animação termina."""
        self.hide()
        self.animation.finished.disconnect()
        self.dismissed.emit()

    def _on_close_clicked(self, event):
        """Callback quando o botão de fechar é clicado."""
        self.hide_with_animation()

    def set_message_type(self, message_type: str):
        """Define o tipo de mensagem (atualiza cores e ícones)."""
        self._message_type = message_type
        self.update()  # Redesenha com nova cor


class NotificationManager:
    """
    Gerenciador de notificações da aplicação.

    Responsabilidades:
    - Gerenciar múltiplas notificações simultâneas
    - Evitar sobreposição excessiva
    - Controlar o tempo de exibição
    - Fornecer interface simples para exibir notificações
    """

    def __init__(self, parent=None):
        self.parent = parent
        self.notifications = []
        self.max_notifications = 3  # Máximo de notificações visíveis simultaneamente

    def show_info(self, message: str, duration: int = 3000):
        """Exibe mensagem de informação."""
        self._show_notification(message, "info", duration)

    def show_success(self, message: str, duration: int = 3000):
        """Exibe mensagem de sucesso."""
        self._show_notification(message, "success", duration)

    def show_error(self, message: str, duration: int = 5000):
        """Exibe mensagem de erro (tempo maior por ser crítico)."""
        self._show_notification(message, "error", duration)

    def show_warning(self, message: str, duration: int = 4000):
        """Exibe mensagem de aviso."""
        self._show_notification(message, "warning", duration)

    def _show_notification(self, message: str, message_type: str, duration: int):
        """Método interno para exibir notificação."""
        # Remove notificações antigas se exceder o limite
        if len(self.notifications) >= self.max_notifications:
            old_notification = self.notifications.pop(0)
            old_notification.hide_with_animation()

        # Cria nova notificação
        notification = ToastNotification(self.parent)
        notification.dismissed.connect(lambda: self._on_notification_dismissed(notification))

        # Posiciona as notificações em pilha
        self._position_notifications()

        # Exibe
        notification.show_message(message, message_type, duration)
        self.notifications.append(notification)

    def _position_notifications(self):
        """Posiciona as notificações em pilha no canto superior direito."""
        if not self.notifications:
            return

        # Calcula posição base
        base_x = 20
        base_y = 20

        # Se tem parent, posiciona no canto superior direito
        if self.parent and hasattr(self.parent, 'rect'):
            parent_rect = self.parent.rect()
            base_x = parent_rect.width() - 320  # 320px de largura do toast

        # Posiciona cada notificação
        for i, notification in enumerate(self.notifications):
            y_offset = i * (notification.height() + 12)
            notification.move(base_x, base_y + y_offset)

    def _on_notification_dismissed(self, notification):
        """Callback quando uma notificação é descartada."""
        if notification in self.notifications:
            self.notifications.remove(notification)

        # Reposiciona as notificações restantes
        self._position_notifications()

    def clear_all(self):
        """Remove todas as notificações."""
        for notification in self.notifications[:]:
            notification.hide_with_animation()

    def set_max_notifications(self, max_count: int):
        """Define o número máximo de notificações simultâneas."""
        self.max_notifications = max_count
        # Remove notificações antigas se necessário
        while len(self.notifications) > self.max_notifications:
            old_notification = self.notifications.pop(0)
            old_notification.hide_with_animation()


class StatusManager:
    """
    Gerenciador de mensagens de status para a barra de status.

    Responsabilidades:
    - Exibir mensagens de status no footer
    - Atualizar progresso global
    - Manter histórico de mensagens recentes
    """

    def __init__(self, footer_widget):
        self.footer = footer_widget
        self.message_history = []
        self.max_history = 10

    def set_status(self, message: str, level: str = "info"):
        """Define a mensagem de status no footer."""
        if self.footer:
            self.footer.set_status(message)

        # Adiciona ao histórico
        self._add_to_history(message, level)

    def set_progress(self, value: int):
        """Define o progresso global no footer."""
        if self.footer:
            self.footer.set_progress(value)

    def clear_status(self):
        """Limpa a mensagem de status."""
        self.set_status("Pronto")

    def _add_to_history(self, message: str, level: str):
        """Adiciona mensagem ao histórico."""
        import datetime
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        self.message_history.append({
            "timestamp": timestamp,
            "message": message,
            "level": level
        })

        # Mantém apenas as últimas mensagens
        if len(self.message_history) > self.max_history:
            self.message_history.pop(0)

    def get_history(self):
        """Retorna o histórico de mensagens."""
        return self.message_history.copy()

    def clear_history(self):
        """Limpa o histórico de mensagens."""
        self.message_history.clear()


class ToastDemo(QWidget):
    """
    Demonstração do sistema de notificações.
    Pode ser usada para testar e validar o comportamento dos toasts.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.notification_manager = NotificationManager(self)

        layout = QVBoxLayout(self)

        # Título
        title = QLabel("Demonstração de Notificações")
        palette = ThemeManager().current_palette
        title.setStyleSheet(f"font-size: 18px; font-weight: bold; color: {palette.text_primary};")

        # Botões de teste
        buttons_layout = QVBoxLayout()

        btn_info = QPushButton("Info (3s)")
        btn_info.clicked.connect(lambda: self.notification_manager.show_info("Esta é uma mensagem de informação."))

        btn_success = QPushButton("Success (3s)")
        btn_success.clicked.connect(lambda: self.notification_manager.show_success("Operação concluída com sucesso!"))

        btn_error = QPushButton("Error (5s)")
        btn_error.clicked.connect(lambda: self.notification_manager.show_error("Ocorreu um erro inesperado."))

        btn_warning = QPushButton("Warning (4s)")
        btn_warning.clicked.connect(lambda: self.notification_manager.show_warning("Atenção: Esta é uma mensagem de aviso."))

        btn_multiple = QPushButton("Múltiplas Notificações")
        btn_multiple.clicked.connect(self._show_multiple_notifications)

        btn_clear = QPushButton("Limpar Todas")
        btn_clear.clicked.connect(self.notification_manager.clear_all)

        buttons_layout.addWidget(btn_info)
        buttons_layout.addWidget(btn_success)
        buttons_layout.addWidget(btn_error)
        buttons_layout.addWidget(btn_warning)
        buttons_layout.addWidget(btn_multiple)
        buttons_layout.addWidget(btn_clear)

        layout.addWidget(title)
        layout.addLayout(buttons_layout)
        layout.addStretch()

    def _show_multiple_notifications(self):
        """Demonstra múltiplas notificações simultâneas."""
        self.notification_manager.show_info("Primeira notificação...")
        self.notification_manager.show_success("Segunda notificação!")
        self.notification_manager.show_warning("Terceira notificação...")
        self.notification_manager.show_error("Quarta notificação (será removida a primeira)")
