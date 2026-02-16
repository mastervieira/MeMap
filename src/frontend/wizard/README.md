# Wizard Module - Arquitetura MVVM

Módulo refatorado do wizard seguindo princípios SOLID e padrão MVVM.

## 📋 Estrutura

```
src/frontend/wizard/
├── models/              # Data models (Phase 1 ✅)
│   ├── form_data.py     # FormData dataclass
│   ├── table_data.py    # TableRowData dataclass
│   └── wizard_state.py  # WizardState & WizardAction enums
│
├── services/            # Business logic (Phase 1 ✅)
│   ├── data_service.py        # CRUD operations
│   ├── calculation_service.py # Calculations
│   ├── validation_service.py  # Validation
│   └── export_service.py      # PDF/Excel export
│
├── viewmodels/          # UI logic (Phase 1 ✅)
│   ├── form_viewmodel.py      # Stage 1 form
│   ├── table_viewmodel.py     # Stage 2 table
│   ├── calendar_viewmodel.py  # Stage 3 calendar
│   └── wizard_coordinator.py  # Main coordinator
│
└── views/               # UI components (Phase 1 ✅)
    ├── wizard_view.py         # Main window
    ├── form_view.py           # Stage 1 UI
    ├── table_view.py          # Stage 2 UI
    └── calendar_view.py       # Stage 3 UI
```

## 🎯 Princípios

### Single Responsibility
- **Models**: Apenas estruturas de dados
- **Services**: Apenas lógica de negócio
- **ViewModels**: Apenas estado e comandos UI
- **Views**: Apenas renderização

### Separation of Concerns
```
User Input → View → ViewModel → Service → Repository → DB
   ↑                    ↓
   └─── Signals/Slots ──┘
```

### Type Safety
- 100% tipado com type hints
- Dataclasses imutáveis (frozen=True) quando possível
- Validação em runtime com __post_init__

## 📦 Models

### FormData
```python
@dataclass(frozen=True)
class FormData:
    quantidade_recibos: int
    recibo_inicio: int
    recibo_fim: int
    zona_primaria: str
    zona_secundaria: str
    total_km: Decimal
```

### TableRowData
```python
@dataclass
class TableRowData:
    dia: int
    dia_semana: str
    tipo: TipoDiaAssiduidade
    recibo_inicio: int | None
    # ... outros campos
```

### WizardState
```python
class WizardState(str, Enum):
    STAGE_1_FORM = "stage_1_form"
    STAGE_2_TABLE = "stage_2_table"
    STAGE_3_CALENDAR = "stage_3_calendar"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
```

## 🔧 Services

### DataService
Responsabilidade: Comunicação com repositório
- `carregar_mapa(mes, ano) -> TabelaTaxas | None`
- `guardar_mapa(tabela) -> None`
- `criar_novo_mapa(mes, ano) -> TabelaTaxas`

### CalculationService
Responsabilidade: Cálculos de negócio
- `calcular_totais_tabela(linhas) -> dict[str, Decimal]`
- `calcular_total_mes(tabela) -> Decimal`
- `converter_com_iva_para_sem_iva(valor, taxa) -> Decimal`

### ValidationService
Responsabilidade: Validação de dados
- `validar_formulario(form_data) -> tuple[bool, list[str]]`
- `validar_linha_tabela(linha) -> tuple[bool, str | None]`
- `validar_recibo(recibo_num) -> bool`

### ExportService
Responsabilidade: Exportação
- `exportar_pdf(tabela, template) -> Path`
- `exportar_excel(tabela) -> Path`
- `gerar_preview(tabela) -> QPixmap`

## 🎨 ViewModels

### FormViewModel
Gerencia estado do formulário (Stage 1)
```python
# Signals
form_data_changed = Signal(object)
validation_error = Signal(str, str)

# Commands (Slots)
@Slot(str, object)
def on_field_changed(field_name, value): ...
```

### TableViewModel
Gerencia tabela de recibos (Stage 2)
```python
# Signals
table_data_changed = Signal(list)
totals_updated = Signal(dict)

# Commands
@Slot(object)
def on_add_row(row_data): ...
```

### CalendarViewModel
Gerencia calendário (Stage 3)
```python
# Signals
date_selected = Signal(QDate)
export_completed = Signal(str)

# Commands
@Slot(QDate)
def on_date_selected(date): ...
```

### WizardCoordinator
Orquestra todos os stages
```python
# Signals
state_changed = Signal(object)
wizard_completed = Signal()

# Commands
@Slot()
def on_next_stage(): ...
```

## 🖼️ Views

Views são **PURAS** - apenas renderizam UI:
- Sem lógica de negócio
- Sem chamadas a BD
- Sem cálculos
- Apenas conectam eventos a ViewModels

```python
class FormView(QWidget):
    def _connect_signals(self):
        # View → ViewModel
        self.field_input.textChanged.connect(
            lambda text: self.viewmodel.on_field_changed("field", text)
        )
        
        # ViewModel → View
        self.viewmodel.validation_error.connect(
            self._on_validation_error
        )
```

## ✅ Phase 1 Status (Concluída)

- [x] Criar estrutura de diretórios
- [x] Definir dataclasses em models/
- [x] Criar assinaturas de serviços
- [x] Criar estrutura de ViewModels
- [x] Criar estrutura de Views
- [x] Criar testes base

## 🚀 Próximas Fases

### Phase 2: Implementar Services
- Extrair lógica do wizard atual
- Implementar DataService
- Implementar CalculationService
- Implementar ValidationService
- Implementar ExportService

### Phase 3: Implementar ViewModels
- Conectar ViewModels com Services
- Implementar lógica de navegação
- Implementar gestão de estado

### Phase 4: Atualizar Views
- Conectar Views com ViewModels
- Implementar UI components
- Testar fluxo completo

### Phase 5: Testes & Validação
- Testes unitários (>80% coverage)
- Testes de integração
- Validar todos os 338+ testes passam

### Phase 6: Limpeza
- Eliminar código legacy
- Atualizar documentação
- Code review final

## 🧪 Testes

```bash
# Executar testes do wizard
pytest tests/frontend/wizard/ -v

# Com coverage
pytest tests/frontend/wizard/ --cov=src/frontend/wizard

# Apenas models
pytest tests/frontend/wizard/test_models.py -v
```

## 📝 Convenções

### Type Hints
- Obrigatórios em todas as funções
- Use `from __future__ import annotations`
- Prefer `list[T]` over `List[T]` (Python 3.10+)

### Docstrings
- PEP257 format
- Google style para parâmetros
- Sempre em classes públicas e métodos públicos

### Line Length
- 79 caracteres (PEP8 strict)
- Use quebras de linha para listas/dicts longos

### Imports
```python
# Standard library
from __future__ import annotations

# Third-party
from PySide6.QtCore import Signal

# Local
from src.frontend.wizard.models import FormData
```

## 🔗 Referências

- [TODO.md](../../../TODO.md) - Plano completo de refatoração
- [.claude/instructions.md](../../../.claude/instructions.md) - Regras do projeto
- [Código Legacy](../viewmodels/wizard_view_model.py) - Para comparação
