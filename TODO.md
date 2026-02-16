# TODO - Refatoração do Wizard

## 📋 Contexto

O wizard atual tem **2286 linhas de código** distribuídas em 3 ficheiros:
- `wizard_view_model.py`: 1083 linhas (31+ métodos)
- `wizard_view.py`: 1101 linhas
- `wizard_logic.py`: 102 linhas

**Problemas atuais**:
- Responsabilidades misturadas (validação, cálculo, dados, UI)
- Difícil de testar isoladamente
- Difícil de adicionar novas funcionalidades
- Código duplicado entre métodos
- Lógica de negócio espalhada

## 🎯 Objetivo

Refatorar o wizard numa arquitetura modular seguindo os princípios SOLID:
- **Single Responsibility**: Cada classe tem uma responsabilidade clara
- **Testabilidade**: Serviços isolados com testes unitários
- **Escalabilidade**: Fácil adicionar novas funcionalidades
- **Manutenibilidade**: Código organizado e documentado

## 🏗️ Arquitetura Proposta

```
src/frontend/wizard/
├── models/              # Data models
│   ├── form_data.py     # FormData dataclass
│   ├── table_data.py    # TableData dataclass
│   └── wizard_state.py  # WizardState enum
├── services/            # Business logic
│   ├── data_service.py        # CRUD operations
│   ├── calculation_service.py # Business calculations
│   ├── validation_service.py  # Data validation
│   └── export_service.py      # PDF/Excel export
├── viewmodels/          # UI logic coordination
│   ├── form_viewmodel.py      # Stage 1 form
│   ├── table_viewmodel.py     # Stage 2 table
│   ├── calendar_viewmodel.py  # Stage 3 calendar
│   └── wizard_coordinator.py  # Main coordinator
└── views/               # UI components
    ├── wizard_view.py         # Main wizard window
    ├── form_view.py           # Stage 1 form UI
    ├── table_view.py          # Stage 2 table UI
    └── calendar_view.py       # Stage 3 calendar UI
```

## 📦 Camada de Serviços

### DataService
**Responsabilidade**: Comunicação com repositório e gestão de dados
- `carregar_mapa(mes, ano) -> TabelaTaxas | None`
- `guardar_mapa(tabela) -> None`
- `criar_novo_mapa(mes, ano) -> TabelaTaxas`
- `eliminar_dia(tabela, dia) -> None`
- `atualizar_wizard_data(tabela, dados) -> None`

### CalculationService
**Responsabilidade**: Cálculos de negócio (totais, conversões, validações matemáticas)
- `calcular_totais_tabela(linhas) -> dict[str, Decimal]`
- `calcular_total_mes(tabela) -> Decimal`
- `converter_com_iva_para_sem_iva(valor, taxa) -> Decimal`
- `calcular_kilometros_totais(dias) -> Decimal`
- `calcular_dias_trabalhados(mes, ano) -> int`

### ValidationService
**Responsabilidade**: Validação de dados de negócio
- `validar_formulario(form_data) -> tuple[bool, list[str]]`
- `validar_linha_tabela(linha) -> tuple[bool, str | None]`
- `validar_recibo(recibo_num) -> bool`
- `validar_datas(mes, ano) -> bool`
- `validar_consistencia_dados(tabela) -> tuple[bool, list[str]]`

### ExportService
**Responsabilidade**: Exportação de dados para PDF/Excel
- `exportar_pdf(tabela, template) -> Path`
- `exportar_excel(tabela) -> Path`
- `gerar_preview(tabela) -> QPixmap`
- `validar_exportacao(tabela) -> tuple[bool, str | None]`

## 🎨 Camada de ViewModels

### FormViewModel
**Responsabilidade**: Lógica do formulário (Stage 1)
- Gestão de estado do formulário
- Validação de campos
- Comunicação com DataService para carregar/guardar

### TableViewModel
**Responsabilidade**: Lógica da tabela de recibos (Stage 2)
- Gestão de linhas da tabela
- Adição/remoção de recibos
- Cálculo de totais via CalculationService

### CalendarViewModel
**Responsabilidade**: Lógica do calendário mensal (Stage 3)
- Gestão de dias trabalhados/ausências
- Validação de datas
- Exportação via ExportService

### WizardCoordinator
**Responsabilidade**: Coordenação entre stages e estado global
- Gestão de transições entre stages
- Estado global do wizard
- Orquestração de serviços

## 📝 Plano de Migração

### Fase 1: Setup Base
1. Criar estrutura de diretórios `src/frontend/wizard/`
2. Criar ficheiros vazios para cada módulo
3. Definir dataclasses em `models/`
4. Criar testes unitários base para cada serviço

### Fase 2: Extrair Serviços
1. **DataService**: Extrair métodos relacionados com repositório
   - `carregar_ou_criar_mapa()`
   - `guardar_mapa()`
   - `eliminar_dia()`

2. **CalculationService**: Extrair cálculos
   - `calcular_totais()`
   - `_calcular_totais_setubal/santarem/evora()`
   - `calcular_total_faturacao()`

3. **ValidationService**: Extrair validações
   - `validar_recibo_duplicado()`
   - `validar_dados_formulario()`
   - Validações de datas

4. **ExportService**: Extrair exportação
   - Métodos de PDF/Excel
   - Preview

### Fase 3: Criar ViewModels Especializados
1. Criar `FormViewModel` com lógica do Stage 1
2. Criar `TableViewModel` com lógica do Stage 2
3. Criar `CalendarViewModel` com lógica do Stage 3
4. Criar `WizardCoordinator` para orquestração

### Fase 4: Atualizar Views
1. Refatorar `wizard_view.py` para usar ViewModels
2. Extrair componentes específicos para `form_view.py`, `table_view.py`, `calendar_view.py`
3. Limpar código duplicado

### Fase 5: Testes e Validação
1. Escrever testes unitários para cada serviço
2. Escrever testes de integração para ViewModels
3. Testar fluxo completo do wizard
4. Validar que todos os 338 testes continuam a passar

### Fase 6: Limpeza
1. Eliminar código antigo comentado
2. Atualizar documentação
3. Refatorar imports no resto da aplicação
4. Code review final

## ✅ Critérios de Sucesso

- [ ] Serviços isolados com responsabilidades claras
- [ ] Cada serviço tem testes unitários (>80% coverage)
- [ ] ViewModels não têm lógica de negócio
- [ ] Views apenas renderizam UI
- [ ] Todos os testes existentes continuam a passar
- [ ] Código reduzido de ~2286 para <1500 linhas
- [ ] Cada ficheiro tem <300 linhas
- [ ] Documentação atualizada

## 🚀 Benefícios Esperados

1. **Testabilidade**: Cada serviço pode ser testado isoladamente
2. **Manutenibilidade**: Responsabilidades claras, fácil encontrar código
3. **Escalabilidade**: Adicionar novas funcionalidades sem quebrar existentes
4. **Reutilização**: Serviços podem ser usados em outras partes da app
5. **Debugging**: Mais fácil isolar problemas
6. **Onboarding**: Novos developers entendem a estrutura rapidamente

## 📚 Referências

- Código existente: `src/frontend/viewmodels/wizard_view_model.py`
- Padrões a seguir: `src/repositories/tabela_taxas_repository.py`
- Testes existentes: `tests/test_wizard.py`
- Validadores: `src/common/validators/`

## 🔄 Próximos Passos

1. Ler e analisar `wizard_view_model.py` linha por linha
2. Mapear todos os métodos para serviços apropriados
3. Criar diagrama de dependências
4. Começar Fase 1: Setup Base

---

**Data de criação**: 2026-02-15
**Estado**: Planeamento
**Prioridade**: Alta
