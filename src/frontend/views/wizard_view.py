"""
Interface do formulário guiado (Wizard) para o MeMap Pro.
Implementa a navegação entre páginas e a estrutura de grids solicitada.
"""

import asyncio
import logging
from typing import Any, Final, Optional
from PySide6.QtCore import Qt, Signal, Slot, QDate
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QStackedWidget, QSizePolicy, QGraphicsOpacityEffect
)
from qasync import asyncSlot

from src.frontend.styles.component_styles import NavbarStyles
from src.db.models.base_mixin import EstadoDocumento

logger = logging.getLogger(__name__)

# Simulação de imports do módulo 'common'
# from common.base import BaseFormPage
# from common.styles import AppColors

from src.frontend.views.wizard_logic import WizardValidator, ZonaTrabalho, ValidationResult, FormPage1Data

# Constantes de Layout
INPUT_WIDTH: Final[int] = 60

class WizardPage1(QWidget):
    """Primeira página do formulário guiado."""

    submitted = Signal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._validator = WizardValidator()
        self._init_ui()

    def _init_ui(self) -> None:
        """Inicializa a interface com duas grids (superior e inferior)."""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(0)

        # --- Grid Superior (Dividida em 2 colunas, cada uma com 4 linhas) ---
        self.upper_frame = QFrame()
        self.upper_frame.setObjectName("upper_grid")
        self.upper_layout = QGridLayout(self.upper_frame)
        self.upper_layout.setContentsMargins(10, 10, 10, 10)
        self.upper_layout.setSpacing(15)

        # Configuração das colunas (50% cada)
        self.upper_layout.setColumnStretch(0, 1)
        self.upper_layout.setColumnStretch(1, 1)

        # Coluna Esquerda (Superior)
        self._setup_left_column()

        # Coluna Direita (Superior) - Espaço reservado para futuras perguntas
        self._setup_right_column()

        # --- Grid Inferior ---
        self.lower_frame = QFrame()
        self.lower_frame.setObjectName("lower_grid")
        self.lower_layout = QVBoxLayout(self.lower_frame)

        # Botão de navegação na grid inferior
        self.btn_next = QPushButton("Próximo ➔")
        self.btn_next.setFixedWidth(120)
        self.btn_next.setMinimumHeight(40)
        self.btn_next.clicked.connect(self._on_next_clicked)
        self.lower_layout.addWidget(self.btn_next, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)

        # Adiciona as grids ao layout principal dividindo o espaço total
        self.main_layout.addWidget(self.upper_frame, 1)
        self.main_layout.addWidget(self.lower_frame, 1)

    def _setup_left_column(self) -> None:
        """Configura a coluna esquerda da grid superior (4 linhas)."""

        # 1ª Linha: Recibos (Quantidade, Início, Fim)
        row1_container = QWidget()
        row1_layout = QHBoxLayout(row1_container)
        row1_layout.setContentsMargins(0, 0, 0, 0)
        row1_layout.setSpacing(10)

        self.input_qtd = self._create_input("Quantos recibos são?", row1_layout)
        self.input_inicio = self._create_input("Início", row1_layout)
        self.input_fim = self._create_input("Fim", row1_layout)
        row1_layout.addStretch()

        self.upper_layout.addWidget(row1_container, 0, 0)

        # 2ª Linha: Zona e KM
        row2_container = QWidget()
        row2_layout = QHBoxLayout(row2_container)
        row2_layout.setContentsMargins(0, 0, 0, 0)
        row2_layout.setSpacing(10)

        self.combo_zona1 = self._create_chosebox("Zona 1", row2_layout)
        self.combo_zona2 = self._create_chosebox("Zona 2", row2_layout)
        self.input_km = self._create_input("Total KM", row2_layout)
        row2_layout.addStretch()

        self.upper_layout.addWidget(row2_container, 1, 0)

        # 3ª e 4ª Linhas: Reservadas (Labels vazios para manter a estrutura de 4 linhas)
        self.upper_layout.addWidget(QLabel(" "), 2, 0)
        self.upper_layout.addWidget(QLabel(" "), 3, 0)

    def _setup_right_column(self) -> None:
        """Configura a coluna direita da grid superior (4 linhas reservadas)."""
        for i in range(4):
            placeholder = QLabel(f" ")
            self.upper_layout.addWidget(placeholder, i, 1)

    def _create_input(self, label_text: str, layout: QHBoxLayout) -> QLineEdit:
        """Cria um par Label + InputBox com largura fixa de 60px."""
        label = QLabel(label_text)
        input_field = QLineEdit()
        input_field.setFixedWidth(INPUT_WIDTH)
        input_field.setPlaceholderText("0")

        layout.addWidget(label)
        layout.addWidget(input_field)
        return input_field

    def _create_chosebox(self, label_text: str, layout: QHBoxLayout) -> QComboBox:
        """Cria um par Label + ChoseBox (ComboBox)."""
        label = QLabel(label_text)
        combo = QComboBox()
        combo.setMinimumWidth(100)

        # Popula com as zonas do Enum
        for zona in ZonaTrabalho:
            combo.addItem(zona.value, zona)

        layout.addWidget(label)
        layout.addWidget(combo)
        return combo

    def _on_next_clicked(self) -> None:
        """Coleta dados, valida e emite sinal para próxima página."""
        raw_data = {
            "quantidade_recibos": self.input_qtd.text(),
            "recibo_inicio": self.input_inicio.text(),
            "recibo_fim": self.input_fim.text(),
            "zona_primaria": self.combo_zona1.currentText(),
            "zona_secundaria": self.combo_zona2.currentText(),
            "total_km": self.input_km.text(),
        }

        result = self._validator.validate_page_1(raw_data)

        if result.is_valid:
            # Reset visual em caso de sucesso prévio
            self.input_qtd.setStyleSheet("")
            self.submitted.emit(result.data)
        else:
            # Feedback visual de erro
            self.input_qtd.setToolTip(result.error_message or "Erro de validação")
            self.input_qtd.setStyleSheet("border: 1px solid #F44747;")

class GuidedFormWizard(QWidget):
    """Widget principal que gerencia a navegação do formulário guiado."""

    # Sinal para atualizar o progresso (0-100)
    loading_progress = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_loading = False
        self._current_state: EstadoDocumento = EstadoDocumento.RASCUNHO

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 10, 20, 20)
        self.main_layout.setSpacing(10)

        # Header para mostrar a data selecionada (Estilo Navbar)
        self.header_frame = QFrame()
        self.header_frame.setObjectName("wizard_header")
        self.header_frame.setStyleSheet(f"""
            QFrame#wizard_header {{
                background-color: #2D2D30;
                border-bottom: 2px solid #007ACC;
                border-radius: 8px;
                padding: 10px;
            }}
        """)
        header_layout = QHBoxLayout(self.header_frame)

        self.date_label = QLabel("Selecione uma data no calendário")
        self.date_label.setStyleSheet(NavbarStyles.get_page_title_style())
        header_layout.addWidget(self.date_label)
        header_layout.addStretch()

        self.main_layout.addWidget(self.header_frame)

        self.stack = QStackedWidget()

        # Páginas do Wizard
        self.page1 = WizardPage1()
        self.page1.submitted.connect(self._next_page)

        self.page2 = QWidget() # Placeholder para a 2ª página
        p2_layout = QVBoxLayout(self.page2)
        p2_layout.addWidget(QLabel("Página 2 - Em desenvolvimento"), 0, Qt.AlignmentFlag.AlignCenter)
        btn_back = QPushButton("⬅ Voltar")
        btn_back.clicked.connect(lambda: self.stack.setCurrentIndex(0))
        p2_layout.addWidget(btn_back, 0, Qt.AlignmentFlag.AlignCenter)

        self.stack.addWidget(self.page1)
        self.stack.addWidget(self.page2)

        self.main_layout.addWidget(self.stack)

    def _next_page(self, data: dict) -> None:
        """Avança para a próxima página do formulário."""
        self.stack.setCurrentIndex(self.stack.currentIndex() + 1)

    def _set_ui_enabled(self, enabled: bool):
        """Habilita/Desabilita a UI durante o carregamento."""
        self.stack.setEnabled(enabled)
        opacity = 1.0 if enabled else 0.5
        effect = QGraphicsOpacityEffect(self.stack)
        effect.setOpacity(opacity)
        self.stack.setGraphicsEffect(effect)

    @asyncSlot(QDate)
    async def set_selected_date(self, date: QDate):
        """
        Slot Assíncrono que carrega dados da DB para a data selecionada.
        Previne race conditions usando uma flag de loading.
        """
        if self._is_loading:
            logger.warning("Carregamento já em curso. Ignorando novo pedido.")
            return

        self._is_loading = True
        self._set_ui_enabled(False)
        self.loading_progress.emit(10)
        self.date_label.setText(f"⏳ A carregar dados para {date.toString('dd/MM/yyyy')}...")

        try:
            # --- SIMULAÇÃO DE CHAMADA À DB (I/O Assíncrono) ---
            # Simulação de progresso incremental
            for i in range(1, 11):
                await asyncio.sleep(0.1)  # Simula latência de rede/DB
                self.loading_progress.emit(10 + (i * 8))  # Vai de 10% a 90%

            # Simulação de lógica de estado baseada no dia
            if date.day() % 2 == 0:
                self._current_state = EstadoDocumento.RASCUNHO
                status_text = "📝 Rascunho (Editável)"
            else:
                self._current_state = EstadoDocumento.FECHADO
                status_text = "🔒 Fechado (Apenas Leitura)"

            # Formata a data em Português
            meses = ["", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
                     "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]

            self.date_label.setText(
                f"📅 {date.day()} de {meses[date.month()]} | {status_text}"
            )

            # Aplica restrições de UI baseadas no estado
            self.page1.setEnabled(self._current_state == EstadoDocumento.RASCUNHO)

            # Resetar o wizard para a primeira página
            self.stack.setCurrentIndex(0)
            self.loading_progress.emit(100)

        except Exception as e:
            logger.error(f"Erro ao carregar dados: {e}")
            self.date_label.setText("❌ Erro ao carregar dados da Base de Dados")
        finally:
            self._is_loading = False
            self._set_ui_enabled(True)
            # Pequeno delay antes de esconder a barra (opcional)
            await asyncio.sleep(0.5)
            self.loading_progress.emit(0)
