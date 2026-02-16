# 🏗️ MeMap Project - Instruções Obrigatórias para Claude

**Status:** MVVM Migration in Progress (Hybrid Architecture)
**Python Version:** 3.14+
**Framework:** PySide6 + qasync
**Pattern:** MVVM (Model-View-ViewModel)

---

## 📋 Índice Rápido
1. [Arquitetura MVVM](#arquitetura-mvvm)
2. [PEP8 & Code Quality](#pep8--code-quality)
3. [Estrutura de Projeto](#estrutura-de-projeto)
4. [Componentes Obrigatórios](#componentes-obrigatórios)
5. [Async & Workers](#async--workers)
6. [UI/UX Guidelines](#uiux-guidelines)
7. [Exemplos Práticos](#exemplos-práticos)

---

## 🏗️ Arquitetura MVVM

### O Padrão MVVM Explicado

```
User Input → View → ViewModel → Model → Data Layer
   ↑                    ↓
   └────── Signals/Slots ────────┘
```

### Camadas (Obrigatório)

#### 1. **Model** - Dados e Lógica de Negócio
```
src/core/
├── models/           # TypedDicts, Pydantic models
├── repositories/     # Data access (DB)
├── services/         # Business logic
└── exceptions/       # Custom exceptions
```

**Responsabilidade:**
- Dados puros (sem conhecimento de UI)
- Validação de regras de negócio
- Comunicação com BD/APIs
- Exceções específicas do domínio

#### 2. **ViewModel** - Estado e Comandos (NOVO!)
```
src/frontend/viewmodels/
├── base_viewmodel.py      # Classe base
├── wizard_viewmodel.py     # Wizard page
├── dashboard_viewmodel.py  # Dashboard
└── ...
```

**Responsibilidades:**
- Gerenciar estado da página
- Processar eventos da View via commands
- Converter dados do Model para formato UI
- Emitir signals para atualizar View
- Validação de entrada da UI
- Coordenar operações assíncronas

**Propriedades Obrigatórias:**
```python
class BaseViewModel(QObject):
    # Signals
    loading = Signal(bool)
    error = Signal(str)
    success = Signal(str)

    # Propriedades
    @property
    def is_loading(self) -> bool: ...

    @property
    def has_errors(self) -> bool: ...
```

#### 3. **View** - Interface (PySide6 Widgets)
```
src/frontend/views/ ou /pages/
├── wizard_page.py
├── dashboard_page.py
└── ...
```

**Responsabilidades:**
- Renderizar UI (widgets PySide6)
- Ligar eventos a commands do ViewModel
- Ligar properties do ViewModel a widgets
- **ZERO lógica de negócio**
- **ZERO chamadas diretas ao Model**

---

## ✅ PEP8 & Code Quality

### Configuração (JÁ APLICADA)
- **Line length:** 79 caracteres (PEP8 strict)
- **Indentation:** 4 espaços
- **Type hints:** Obrigatórios em todas funções
- **Docstrings:** PEP257 em classes e funções públicas

### Ferramentas de Qualidade
```bash
# Format
poetry run black src/ --line-length 79
poetry run isort src/ --profile black

# Lint
poetry run flake8 src/
poetry run mypy src/ --strict
poetry run pylint src/

# Testes
poetry run pytest tests/ --cov=src
```

### Padrões de Código Obrigatórios

#### Type Hints (OBRIGATÓRIO)
```python
from src.core.models import UserModel

def process_wizard_data(
    data: dict[str, str],
    user_id: int,
) -> dict[str, object] | None:
    """Process wizard form data.

    Args:
        data: Form input data
        user_id: User identifier

    Returns:
        Validation result or None if error
    """
```

#### Docstrings (PEP257)
```python
class WizardViewModel(BaseViewModel):
    """Manages wizard page state and logic.

    This ViewModel handles form validation, data processing,
    and communication with the database layer.

    Signals:
        page_completed: Emitted when page is complete
        validation_error: Emitted when validation fails
    """
```

#### Imports Ordering (via isort)
```python
# Standard library
import json
from typing import Dict, Optional

# Third-party
from PySide6.QtCore import QObject, Signal, Slot

# Local
from src.core.models import UserModel
from src.frontend.viewmodels import BaseViewModel
```

---

## 📁 Estrutura de Projeto

### Atual (Com Migração MVVM)
```
MeMap/
├── src/
│   ├── core/                    # Lógica de negócio (Model)
│   │   ├── models/              # TypedDicts, Pydantic
│   │   │   ├── user.py
│   │   │   ├── mapa.py
│   │   │   └── schemas.py       # Pydantic schemas
│   │   ├── repositories/        # Data access
│   │   │   ├── base_repository.py
│   │   │   ├── user_repository.py
│   │   │   └── mapa_repository.py
│   │   ├── services/            # Business logic
│   │   │   ├── wizard_service.py
│   │   │   └── mapa_service.py
│   │   └── exceptions/          # Custom exceptions
│   │       └── domain_exceptions.py
│   │
│   ├── frontend/                # Apresentação (View + ViewModel)
│   │   ├── viewmodels/          # ⭐ NOVO - MVVM
│   │   │   ├── __init__.py
│   │   │   ├── base_viewmodel.py
│   │   │   ├── wizard_viewmodel.py
│   │   │   ├── dashboard_viewmodel.py
│   │   │   └── calendar_viewmodel.py
│   │   │
│   │   ├── views/               # View puros (sem lógica)
│   │   │   ├── main_view.py
│   │   │   ├── sidebar.py
│   │   │   ├── navbar.py
│   │   │   └── footer.py
│   │   │
│   │   ├── pages/               # Páginas (View compostas)
│   │   │   ├── wizard_page.py
│   │   │   ├── dashboard_page.py
│   │   │   ├── calendar_page.py
│   │   │   └── ...
│   │   │
│   │   ├── styles/              # Estilos QSS
│   │   │   ├── theme.py
│   │   │   ├── colors.py
│   │   │   └── style_manager.py
│   │   │
│   │   ├── widgets/             # Componentes reutilizáveis
│   │   │   ├── custom_button.py
│   │   │   ├── custom_card.py
│   │   │   └── ...
│   │   │
│   │   ├── workers/             # Async workers (qasync)
│   │   │   ├── base_worker.py
│   │   │   └── data_worker.py
│   │   │
│   │   └── controllers/         # 🔴 LEGACY (deprecate gradualmente)
│   │       └── calendar_controller.py
│   │
│   ├── db/                      # Database
│   │   ├── __init__.py
│   │   └── models/              # SQLAlchemy ORM models
│   │       ├── user.py
│   │       └── mapa.py
│   │
│   └── main.py                  # Entry point
│
├── tests/                       # Testes
│   ├── test_core/
│   ├── test_frontend/
│   └── conftest.py
│
├── docs/
│   ├── development_guidelines.md
│   └── architecture.md
│
├── .claude/
│   ├── instructions.md          # Este ficheiro
│   └── mvvm_examples.md         # Exemplos práticos
│
├── .vscode/
│   ├── settings.json
│   ├── tasks.json
│   ├── launch.json
│   └── extensions.json
│
├── .flake8
├── .editorconfig
├── pyproject.toml
└── README.md
```

---

## 🔒 Segurança & Estabilidade (Implementação Pragmática)

### 1. Logging Centralizado (FAZER AGORA)

**Ficheiro:** `src/common/logging_config.py`

```python
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_file: str = "memap.log") -> None:
    """Setup centralized logging with rotation."""
    log_path = Path(log_file)

    handler = logging.handlers.RotatingFileHandler(
        log_path,
        maxBytes=10_000_000,  # 10MB
        backupCount=5,
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logging.basicConfig(
        level=logging.INFO,
        handlers=[handler],
    )

# Capture uncaught exceptions
def setup_exception_hook() -> None:
    """Capture crashes to log file."""
    import sys

    def log_uncaught(exc_type, exc_value, traceback):
        logging.critical(
            "Uncaught exception",
            exc_info=(exc_type, exc_value, traceback)
        )

    sys.excepthook = log_uncaught
```

**Uso em `src/main.py`:**
```python
from src.common.logging_config import setup_logging, setup_exception_hook

setup_logging()
setup_exception_hook()
```

---

### 2. BaseValidator Pattern (IMPLEMENTAR NA 2ª VALIDAÇÃO)

**Ficheiro:** `src/common/validators/base_validator.py`

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseValidator(ABC):
    """Base class for all validators."""

    @abstractmethod
    def is_valid(self, data: Any) -> bool:
        """Validate data. Must be implemented by subclass."""
        pass

    @abstractmethod
    def get_errors(self) -> Dict[str, str]:
        """Return validation errors."""
        pass
```

**Exemplo de Validador Concreto:**
```python
# src/common/validators/wizard_validator.py

from typing import Dict
from .base_validator import BaseValidator

class WizardValidator(BaseValidator):
    """Validates wizard form data."""

    def __init__(self) -> None:
        self._errors: Dict[str, str] = {}

    def is_valid(self, data: Dict[str, str]) -> bool:
        """Validate form data."""
        self._errors = {}

        if not data.get("email"):
            self._errors["email"] = "Email required"
        if not data.get("name"):
            self._errors["name"] = "Name required"

        return len(self._errors) == 0

    def get_errors(self) -> Dict[str, str]:
        """Return validation errors."""
        return self._errors
```

---

### 3. Pillow Image Sanitization (COM CACHE)

**Ficheiro:** `src/common/utils/image_sanitizer.py`

```python
import hashlib
from pathlib import Path
from typing import Optional
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class ImageSanitizer:
    """Sanitize images (remove metadata, prevent attacks)."""

    CACHE_DIR = Path("./cache/images")
    ALLOWED_FORMATS = {"JPEG", "PNG", "GIF", "BMP"}

    def __init__(self) -> None:
        self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

    def sanitize(
        self,
        file_path: Path,
    ) -> Optional[Path]:
        """Sanitize image and return cached path."""
        try:
            # Check cache first
            cache_path = self._get_cache_path(file_path)
            if cache_path.exists():
                logger.info(f"Cache hit: {cache_path}")
                return cache_path

            # Open and re-encode (removes metadata)
            image = Image.open(file_path)

            # Validate format
            if image.format not in self.ALLOWED_FORMATS:
                logger.warning(
                    f"Invalid format: {image.format}"
                )
                return None

            # Save to cache (re-encoding removes metadata)
            fmt = image.format or "PNG"
            image.save(cache_path, format=fmt)
            logger.info(f"Sanitized: {cache_path}")

            return cache_path

        except Exception as e:
            logger.error(f"Sanitization failed: {e}")
            return None

    def _get_cache_path(self, file_path: Path) -> Path:
        """Generate cache filename based on file hash."""
        file_hash = hashlib.md5(
            str(file_path).encode()
        ).hexdigest()
        return self.CACHE_DIR / f"{file_hash}.png"
```

**Uso:**
```python
sanitizer = ImageSanitizer()
safe_path = sanitizer.sanitize(Path("user_image.jpg"))
```

---

## 🔧 Componentes Obrigatórios

### 1. BaseViewModel (Classe Mãe)

```python
# src/frontend/viewmodels/base_viewmodel.py

from PySide6.QtCore import QObject, Signal, Slot, Property
from typing import Any
import logging

logger = logging.getLogger(__name__)


class BaseViewModel(QObject):
    """Base class for all ViewModels.

    Provides common signals, properties, and methods for
    managing UI state and communication with models.
    """

    # Signals
    loading = Signal(bool)              # Loading state changed
    error = Signal(str)                 # Error occurred
    success = Signal(str)               # Success message
    data_changed = Signal()             # Data was updated

    def __init__(self, parent: Any = None) -> None:
        super().__init__(parent)
        self._is_loading = False
        self._error_message = ""
        self._success_message = ""

    # Properties
    @Property(bool)
    def is_loading(self) -> bool:
        """Whether ViewModel is currently loading."""
        return self._is_loading

    @is_loading.setter
    def is_loading(self, value: bool) -> None:
        if self._is_loading != value:
            self._is_loading = value
            self.loading.emit(value)

    @Property(str)
    def error_message(self) -> str:
        """Current error message."""
        return self._error_message

    @error_message.setter
    def error_message(self, value: str) -> None:
        self._error_message = value
        if value:
            self.error.emit(value)
            logger.error(f"ViewModel error: {value}")

    # Commands (slots called from View)
    @Slot()
    def on_initialization(self) -> None:
        """Called when View is initialized."""
        pass

    @Slot()
    def on_cleanup(self) -> None:
        """Called when View is destroyed."""
        pass
```

### 2. Exemplo de ViewModel Concreto

```python
# src/frontend/viewmodels/wizard_viewmodel.py

from PySide6.QtCore import Signal, Slot
from typing import Dict, Optional
from src.core.models import WizardData
from src.core.services import WizardService
from .base_viewmodel import BaseViewModel


class WizardViewModel(BaseViewModel):
    """Manages wizard form state and validation."""

    # Signals específicos
    page_changed = Signal(int)          # Page number
    validation_error = Signal(str)      # Field name
    submit_success = Signal()           # Form submitted

    def __init__(self, wizard_service: WizardService) -> None:
        super().__init__()
        self._service = wizard_service
        self._current_page = 0
        self._form_data: Dict[str, str] = {}

    @property
    def current_page(self) -> int:
        return self._current_page

    # Commands from View
    @Slot(str, str)
    def on_field_changed(
        self,
        field_name: str,
        value: str,
    ) -> None:
        """Called when user edits a form field."""
        self._form_data[field_name] = value

        # Validação real-time
        if not self._service.validate_field(field_name, value):
            self.validation_error.emit(field_name)

    @Slot()
    def on_next_page(self) -> None:
        """Navigate to next page."""
        if self._service.validate_page(self._current_page):
            self._current_page += 1
            self.page_changed.emit(self._current_page)
        else:
            self.error_message = "Complete required fields"

    @Slot()
    def on_submit(self) -> None:
        """Submit form to database."""
        self.is_loading = True
        try:
            result = self._service.save_wizard_data(
                self._form_data
            )
            self.submit_success.emit()
        except Exception as e:
            self.error_message = str(e)
        finally:
            self.is_loading = False
```

### 3. Exemplo de View Conectado a ViewModel

```python
# src/frontend/pages/wizard_page.py

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
)
from PySide6.QtCore import Slot
from src.frontend.viewmodels import WizardViewModel


class WizardPage(QWidget):
    """Wizard form page (PURE VIEW - sem lógica)."""

    def __init__(
        self,
        viewmodel: WizardViewModel,
    ) -> None:
        super().__init__()
        self.viewmodel = viewmodel
        self._init_ui()
        self._connect_signals()

    def _init_ui(self) -> None:
        """Initialize UI components."""
        layout = QVBoxLayout()

        self.field_input = QLineEdit()
        layout.addWidget(self.field_input)

        self.submit_btn = QPushButton("Next")
        layout.addWidget(self.submit_btn)

        self.setLayout(layout)

    def _connect_signals(self) -> None:
        """Connect View signals to ViewModel commands."""

        # View → ViewModel (commands)
        self.field_input.textChanged.connect(
            self._on_field_changed
        )
        self.submit_btn.clicked.connect(
            self.viewmodel.on_next_page
        )

        # ViewModel → View (updates)
        self.viewmodel.validation_error.connect(
            self._on_validation_error
        )
        self.viewmodel.loading.connect(
            self._on_loading_changed
        )

    @Slot(str)
    def _on_field_changed(self, text: str) -> None:
        """User edited field."""
        self.viewmodel.on_field_changed("field_name", text)

    @Slot(str)
    def _on_validation_error(self, field: str) -> None:
        """Show validation error in UI."""
        self.field_input.setStyleSheet("border: 1px solid red;")

    @Slot(bool)
    def _on_loading_changed(self, loading: bool) -> None:
        """Update loading state in UI."""
        self.submit_btn.setEnabled(not loading)
```

---

## ⚡ Async & Workers

### Padrão Obrigatório com qasync

```python
# src/frontend/workers/data_worker.py

from qasync import asyncSlot
from PySide6.QtCore import QObject, Signal
import asyncio


class DataWorker(QObject):
    """Worker for async operations."""

    finished = Signal(object)
    error = Signal(str)

    @asyncSlot()
    async def fetch_data(self, user_id: int) -> None:
        """Fetch data asynchronously."""
        try:
            # Operação async
            result = await self._async_fetch(user_id)
            self.finished.emit(result)
        except Exception as e:
            self.error.emit(str(e))

    async def _async_fetch(self, user_id: int) -> dict:
        """Simulated async operation."""
        await asyncio.sleep(1)
        return {"user_id": user_id, "data": []}
```

### No ViewModel

```python
@Slot()
async def on_load_data(self) -> None:
    """Load data from database."""
    self.is_loading = True
    try:
        data = await self._service.fetch_user_data()
        self._process_data(data)
        self.data_changed.emit()
    except Exception as e:
        self.error_message = str(e)
    finally:
        self.is_loading = False
```

---

## 🎨 UI/UX Guidelines

### Design System (Atomic Components)

**Componentes Reutilizáveis:**
```
src/frontend/widgets/
├── buttons/
│   ├── primary_button.py      # Action buttons
│   └── secondary_button.py
├── inputs/
│   ├── text_input.py          # Custom QLineEdit
│   └── combo_box.py
├── displays/
│   ├── card.py                # Content containers
│   ├── badge.py               # Status indicators
│   └── toast.py               # Notifications
└── layouts/
    └── responsive_grid.py
```

### Cores e Tema

```python
# src/frontend/styles/colors.py

class ThemeColors:
    """Color palette for light and dark modes."""

    # Light mode
    PRIMARY = "#007AFF"
    SECONDARY = "#5AC8FA"
    BACKGROUND = "#F5F5F7"
    SURFACE = "#FFFFFF"
    ERROR = "#FF3B30"

    # Dark mode
    DARK_PRIMARY = "#0A84FF"
    DARK_BACKGROUND = "#1C1C1E"
    DARK_SURFACE = "#2C2C2E"
```

### Validação Visual em Real-Time

```python
def _on_validation_error(self, field: str) -> None:
    """Show visual feedback for invalid field."""
    if field == "email":
        self.email_input.setStyleSheet(
            "QLineEdit { border: 2px solid red; "
            "border-radius: 4px; }"
        )
        self.email_error_label.setText("Invalid email format")
        self.email_error_label.setVisible(True)
```

### Acessibilidade Obrigatória

```python
# Keyboard shortcuts
self.shortcut_save = QShortcut(QKeySequence.Save, self)
self.shortcut_save.activated.connect(self.on_save)

# Tab order
self.setTabOrder(self.field1, self.field2)
self.setTabOrder(self.field2, self.submit_btn)
```

---

## 📚 Exemplos Práticos

### Migration Path Recomendado

#### 1️⃣ Primeira Página (Wizard)

**Passo 1: Criar WizardViewModel**
```bash
# View → ViewModel → Model
WizardPage (PURE VIEW)
    ↓ (commands)
WizardViewModel (STATE + LOGIC)
    ↓ (calls)
WizardService (BUSINESS LOGIC)
    ↓ (calls)
WizardRepository (DATA ACCESS)
    ↓ (query)
Database
```

**Passo 2: Remover Lógica da View**
- Remover `WizardValidator` calls diretos
- Remover `set_selected_date` com simulação de BD
- Mover tudo para ViewModel

**Passo 3: Conectar Signals**
- View emite: field changes
- ViewModel recebe, processa, emite updates
- View atualiza UI baseado em signals

#### 2️⃣ Páginas Subsequentes

Repetir o mesmo padrão para:
- DashboardPage → DashboardViewModel
- CalendarPage → CalendarViewModel
- TasksPage → TasksViewModel

---

## ⚠️ Erros Comuns a Evitar

### ❌ NÃO FAZER

```python
# ❌ Lógica na View
class WizardPage(QWidget):
    def on_submit(self):
        self.db.insert_data(self.form_data)  # ❌ ERRADO!
        self.update_ui()

# ❌ View conhece Model
from src.db.models import User  # ❌ ERRADO!

# ❌ ViewModel com widgets
class WizardViewModel(BaseViewModel):
    def update_label(self, label: QLabel):  # ❌ ERRADO!
        label.setText("value")

# ❌ Type hints faltando
def process_data(data):  # ❌ ERRADO!
    return data
```

### ✅ FAZER

```python
# ✅ Lógica no ViewModel
@Slot()
def on_submit(self) -> None:
    self.viewmodel.on_submit_clicked()

# ✅ ViewModel retorna dados
class WizardViewModel(BaseViewModel):
    @property
    def form_data(self) -> Dict[str, str]:
        return self._form_data

# ✅ Type hints obrigatórios
def process_data(data: Dict[str, Any]) -> bool:
    return True
```

---

## 🔍 Checklist para Cada Nova Feature

- [ ] Criar Model (TypedDict ou Pydantic)
- [ ] Criar Service com lógica de negócio
- [ ] Criar Repository para acesso a dados
- [ ] **Criar ViewModel** (herda de BaseViewModel)
- [ ] **Criar View puro** (sem lógica)
- [ ] Ligar View signals → ViewModel commands
- [ ] Ligar ViewModel signals → View updates
- [ ] Adicionar type hints em tudo
- [ ] Escrever docstrings (PEP257)
- [ ] Testar com pytest
- [ ] Passar flake8, mypy, pylint
- [ ] Remover código legacy se existir

---

## 📖 Recursos

- [MVVM Pattern](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)
- [PySide6 Docs](https://doc.qt.io/qtforpython/)
- [PEP8](https://pep8.org/)
- [qasync Documentation](https://github.com/CogentlApps/qasync)
- [Development Guidelines](./docs/development_guidelines.md)

---

## 📝 Notas Importantes

### Para Agentes Claude
1. **SEMPRE** siga a estrutura MVVM
2. **SEMPRE** adicione type hints
3. **NUNCA** coloque lógica nas Views
4. **NUNCA** ignore avisos do linter
5. **SEMPRE** escreva docstrings
6. **SEMPRE** crie testes para features novas

### Estrutura Híbrida
- ✅ Código novo: MVVM completo
- 🟡 Código antigo: coexiste (controllers/) durante transição
- 🔴 Legacy: marque com `# TODO: Migrate to MVVM`

### Testes Obrigatórios
```bash
# Antes de fazer commit
poetry run pytest tests/ --cov=src
poetry run flake8 src/ tests/
poetry run mypy src/ --strict
```

---

## 🚀 Roadmap de Migração MVVM (Pragmático)

### Fase 1: Fundações (1-2 dias)
- [ ] Criar `src/frontend/viewmodels/base_viewmodel.py` (BaseViewModel)
- [ ] Implementar logging centralizado (30min)
- [ ] Estruturar `src/common/validators/` com BaseValidator
- [ ] Adicionar Pillow sanitização

**Entrega:** Estrutura pronta para primeira página MVVM

---

### Fase 2: Primeira Página - Wizard (3-5 dias)
**Por que Wizard primeiro?**
- ✅ Mais isolado (não depende de outras páginas)
- ✅ Tem validação complexa (bom para aprender MVVM)
- ✅ Já tem lógica que pode ser extraída

**Passo a Passo:**

1. **Criar WizardViewModel**
   ```
   src/frontend/viewmodels/wizard_viewmodel.py
   - Herda BaseViewModel
   - Métodos: on_field_changed, on_next_page, on_submit
   - Signals: page_changed, validation_error, submit_success
   ```

2. **Refatorar WizardPage**
   ```
   src/frontend/pages/wizard_page.py
   - Remover lógica (validação, DB, etc)
   - Injetar WizardViewModel no __init__
   - Conectar signals/slots
   ```

3. **Mover Lógica para Services/Repositories**
   ```
   src/core/services/wizard_service.py (validação, DB save)
   src/core/repositories/wizard_repository.py (acesso a BD)
   ```

4. **Testar**
   ```
   pytest tests/frontend/test_wizard_viewmodel.py
   pytest tests/core/test_wizard_service.py
   ```

---

### Fase 3: Outras Páginas (2 dias cada)

**Dashboard:**
- Criar DashboardViewModel
- Remover lógica de MainView
- Mover estado para ViewModel

**Calendar:**
- Destruir CalendarController (legacy)
- Criar CalendarViewModel
- Remover acoplamento de views

**Tasks/Analytics:**
- Repetir padrão

---

### Checklist Pré-Implementação

Antes de começar qualquer página:

```
Logging & Security
- [X] Logging configurado em src/main.py
- [X] sys.excepthook captura crashes
- [X] Tests executam com coverage

Wizard MVVM
- [ ] BaseViewModel criada e testada
- [ ] WizardViewModel implementada
- [ ] WizardPage refatorada (view puro)
- [ ] Sinais conectados corretamente
- [ ] Testes passam (flake8, mypy, pytest)

Code Quality
- [ ] Sem avisos de linter
- [ ] 80%+ coverage nos ViewModels
- [ ] Docstrings em classes públicas
```

---

## 📌 Ordern de Implementação Recomendada

```
DIA 1-2: Setup Segurança
├── Logging centralizado
├── BaseValidator pattern
├── Pillow sanitização
└── Tests para cada componente

DIA 3-4: BaseViewModel
├── Criar classe base
├── Implementar signals/properties
├── Documentação com exemplos
└── Tests unitários

DIA 5-7: Wizard MVVM
├── WizardViewModel completa
├── Refatorar WizardPage
├── Integrar services/repositories
├── Tests (unit + integration)

DIA 8+: Outras Páginas (incrementally)
├── Dashboard → DashboardViewModel
├── Calendar → CalendarViewModel
└── ... (uma de cada vez)
```

---

**Última atualização:** 2026-02-02
**Versão:** 1.1 - MVVM + Security Pragmatic
