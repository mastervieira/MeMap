"""
Widget customizado para a coluna Partilhado da tabela de recibos.
Contém checkbox e sub-colunas expandíveis para seleção de técnicos.
"""

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

# Lista estática de técnicos (temporário - depois virá do banco)
TECNICOS = [
    "Carlos",
    "João Silva",
    "Maria Santos",
    "Pedro Oliveira",
    "Ana Costa",
]


class PartilhadoWidget(QWidget):
    """Widget para célula de partilha com checkbox e seleção de técnicos.

    Features:
    - Checkbox para ativar partilha
    - Quando ativado, mostra 2 sub-colunas (20% e 30%)
    - Cada sub-coluna tem apenas um ComboBox de técnico
    """

    # Signal emitido quando dados mudam
    value_changed = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Configura a interface do widget."""
        # Layout principal vertical
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(5, 2, 5, 2)
        main_layout.setSpacing(5)

        # Define fundo branco do widget
        self.setStyleSheet("""
            PartilhadoWidget {
                background-color: white;
            }
            QCheckBox {
                color: black;
                background-color: white;
            }
            QComboBox {
                background-color: white;
                color: black;
                border: 1px solid #e0e0e0;
            }
            QLabel {
                color: #999;
                background-color: white;
            }
        """)

        # Checkbox principal
        self._checkbox = QCheckBox("Partilhado")
        self._checkbox.stateChanged.connect(self._on_checkbox_changed)
        main_layout.addWidget(self._checkbox, alignment=Qt.AlignmentFlag.AlignCenter)

        # Container para sub-colunas (inicialmente oculto)
        self._fields_container = QWidget()
        container_layout = QHBoxLayout(self._fields_container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(5)

        # ComboBox 20%
        self._combo_20 = QComboBox()
        self._combo_20.setPlaceholderText("20%")
        self._combo_20.addItems(TECNICOS)
        self._combo_20.currentIndexChanged.connect(self._on_value_changed)
        container_layout.addWidget(self._combo_20, stretch=1)

        # Separador visual
        separator = QLabel("|")
        separator.setAlignment(Qt.AlignmentFlag.AlignCenter)
        separator.setStyleSheet("color: #ccc; font-weight: bold;")
        container_layout.addWidget(separator)

        # ComboBox 30%
        self._combo_30 = QComboBox()
        self._combo_30.setPlaceholderText("30%")
        self._combo_30.addItems(TECNICOS)
        self._combo_30.currentIndexChanged.connect(self._on_value_changed)
        container_layout.addWidget(self._combo_30, stretch=1)

        # Botão fechar (✕)
        self._close_btn = QPushButton("✕")
        self._close_btn.setFixedSize(24, 24)
        self._close_btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: none;
                color: #d32f2f;
                font-weight: bold;
                font-size: 18px;
                padding: 0px;
            }
            QPushButton:hover {
                color: #ff1744;
                background-color: #fff0f0;
            }
        """)
        self._close_btn.clicked.connect(self._on_close_clicked)
        container_layout.addWidget(self._close_btn)

        self._fields_container.hide()
        main_layout.addWidget(self._fields_container)

    def _on_checkbox_changed(self, state: int) -> None:
        """Callback quando checkbox é alterado."""
        is_checked = state == Qt.CheckState.Checked.value

        if is_checked:
            # Oculta checkbox e mostra sub-colunas
            self._checkbox.hide()
            self._fields_container.show()
        else:
            # Mostra checkbox e oculta sub-colunas
            self._fields_container.hide()
            self._checkbox.show()
            # Limpa campos ao desmarcar (mostra placeholder)
            self._combo_20.setCurrentIndex(-1)
            self._combo_30.setCurrentIndex(-1)

        self._on_value_changed()

    def _on_value_changed(self) -> None:
        """Emite signal de mudança."""
        self.value_changed.emit()

    def _on_close_clicked(self) -> None:
        """Callback quando botão fechar é clicado."""
        self.set_checked(False)

    def is_checked(self) -> bool:
        """Retorna se checkbox está marcado."""
        return self._checkbox.isChecked()

    def set_checked(self, checked: bool) -> None:
        """Define estado do checkbox."""
        self._checkbox.setChecked(checked)

    def get_tecnico_20(self) -> str:
        """Retorna técnico selecionado no campo 20%."""
        return self._combo_20.currentText()

    def get_tecnico_30(self) -> str:
        """Retorna técnico selecionado no campo 30%."""
        return self._combo_30.currentText()

    def get_data(self) -> dict[str, bool | str]:
        """Retorna dados estruturados do widget.

        Returns:
            Dicionário com dados de partilha
        """
        if not self.is_checked():
            return {
                "partilhado": False,
                "tecnico_20": "",
                "tecnico_30": "",
            }

        return {
            "partilhado": True,
            "tecnico_20": self.get_tecnico_20(),
            "tecnico_30": self.get_tecnico_30(),
        }

    def set_data(self, data: dict) -> None:
        """Define dados do widget.

        Args:
            data: Dicionário com dados de partilha
        """
        self.blockSignals(True)

        is_partilhado = data.get("partilhado", False)
        self.set_checked(is_partilhado)

        if is_partilhado:
            # Define técnicos
            tecnico_20 = data.get("tecnico_20", "")
            tecnico_30 = data.get("tecnico_30", "")

            if tecnico_20 and tecnico_20 in TECNICOS:
                self._combo_20.setCurrentText(tecnico_20)
            else:
                self._combo_20.setCurrentIndex(0)

            if tecnico_30 and tecnico_30 in TECNICOS:
                self._combo_30.setCurrentText(tecnico_30)
            else:
                self._combo_30.setCurrentIndex(0)

        self.blockSignals(False)

    def set_enabled(self, enabled: bool) -> None:
        """Habilita/desabilita o widget."""
        self._checkbox.setEnabled(enabled)
        self._combo_20.setEnabled(enabled)
        self._combo_30.setEnabled(enabled)
