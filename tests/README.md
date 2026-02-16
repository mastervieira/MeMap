# Testes do MeMap

Este diretório contém a suíte de testes para o sistema MeMap, cobrindo modelos, repositórios, integração e utilitários.

## Estrutura dos Testes

```
src/tests/
├── conftest.py              # Configuração do pytest e fixtures
├── test_models.py           # Testes para modelos de banco de dados
├── test_repositories.py     # Testes para repositórios
├── test_integration.py      # Testes de integração
├── test_documentos.py       # Testes específicos para Documentos
├── test_utils.py           # Testes para utilitários e validações
└── README.md               # Este arquivo
```

## Modelos Testados

### User
- Criação com dados válidos/inválidos
- Validação de campos obrigatórios
- Integridade de dados (unique constraints)
- Relacionamentos

### Documento
- Criação com dados mínimos
- Validação de campos obrigatórios
- Integridade de hash SHA256
- Relacionamentos com usuários
- Operações CRUD

### TabelaTaxas
- Criação com validação de mês/ano
- Cálculo de totais a partir de linhas
- Transições de estado
- Relacionamento com linhas

### TabelaTaxasLinha
- Criação com tipos de dia
- Validação de dados
- Relacionamento com tabela

### MapaTaxas
- Criação e cálculo de totais
- Operações com linhas
- Validação de dados

### MapaTaxasLinha
- Criação e validação
- Cálculo de total_faturacao
- Relacionamento com mapa

## Repositórios Testados

### TabelaTaxasRepository
- Operações CRUD
- Validação de dados
- Gestão de dias (linhas)
- Cálculo de totais
- Transições de estado

### MapaTaxasRepository
- Operações CRUD
- Gestão de linhas
- Cálculo de totais
- Exportação PDF

## Testes de Integração

### Fluxos Completos
- Criação → manipulação → finalização de mapas
- Integração entre repositórios
- Validação de fluxos de trabalho

### Erros e Exceções
- Tratamento de dados inválidos
- Operações em entidades inexistentes
- Integridade referencial

## Testes de Utilitários

### ExcelValidator
- Validação de arquivos Excel
- Verificação de colunas obrigatórias
- Validação de dados numéricos

### PDFExporter
- Exportação de mapas para PDF
- Tratamento de erros de arquivo
- Formato de saída

### NotificationManager
- Envio de notificações
- Formatação de mensagens
- Níveis de log

## Como Executar os Testes

### Requisitos
```bash
pip install pytest pytest-cov
```

### Execução Básica
```bash
# Executar todos os testes
pytest src/tests/

# Executar com cobertura
pytest src/tests/ --cov=src --cov-report=html

# Executar testes específicos
pytest src/tests/test_models.py
pytest src/tests/test_repositories.py
pytest src/tests/test_integration.py
```

### Execução com Opções
```bash
# Verbose output
pytest src/tests/ -v

# Paralelizar execução
pytest src/tests/ -n auto

# Executar apenas testes que falharam
pytest src/tests/ --lf

# Executar testes com nomes que contenham "validacao"
pytest src/tests/ -k "validacao"
```

## Cobertura de Testes

Os testes cobrem:
- ✅ Modelos de banco de dados (100%)
- ✅ Repositórios (100%)
- ✅ Integração entre componentes
- ✅ Tratamento de erros e exceções
- ✅ Validações de dados
- ✅ Utilitários e helpers

## Mocks e Fixtures

### Fixtures Principais
- `engine`: Engine SQLite em memória
- `session`: Sessão de banco de dados para cada teste
- `tabela_taxas_repo`: Repositório de Tabela de Taxas
- `mapa_taxas_repo`: Repositório de Mapa de Taxas
- `user_data`: Dados de exemplo para usuário
- `tabela_taxas_data`: Dados de exemplo para tabela de taxas
- `mapa_taxas_data`: Dados de exemplo para mapa de taxas
- `documento_data`: Dados de exemplo para documento

### Mocks Utilizados
- `openpyxl.load_workbook`: Para testes de validação Excel
- `common.utils.notification.logger`: Para testes de notificações
- `tempfile.TemporaryDirectory`: Para testes de exportação PDF

## Padrões de Testes

### Estrutura dos Testes
```python
class TestClasse:
    def test_descricao_clara(self, fixtures):
        # Arrange (Preparação)
        dados = {...}

        # Act (Ação)
        resultado = operacao(dados)

        # Assert (Verificação)
        assert resultado == esperado
```

### Nomenclatura
- Classes: `Test[NomeDaClasse]`
- Métodos: `test_[descricao_clara]`
- Descrições: Verbos no infinitivo, claro e conciso

### Boas Práticas
- Cada teste é independente
- Uso de fixtures para setup
- Mocks para dependências externas
- Asserts claros e específicos
- Tratamento de exceções esperadas

## Relatórios de Testes

### HTML Coverage
Após executar com `--cov-report=html`, abra `htmlcov/index.html` para visualizar:
- Cobertura por arquivo
- Linhas não cobertas
- Métricas de cobertura

### JUnit XML
Para integração com CI/CD:
```bash
pytest src/tests/ --junitxml=results.xml
```

## Troubleshooting

### Erros Comuns
1. **ImportError**: Verifique se as dependências estão instaladas
2. **DatabaseError**: Verifique se o banco de dados em memória está funcionando
3. **MockError**: Verifique se os mocks estão configurados corretamente

### Debug
```bash
# Executar com debug
pytest src/tests/ -v -s

# Executar um teste específico com debug
pytest src/tests/test_models.py::TestUser::test_criar_usuario_valido -v -s
```

## Contribuição

Ao adicionar novos testes:
1. Siga a estrutura existente
2. Use fixtures quando possível
3. Adicione mocks para dependências externas
4. Escreva testes claros e descritivos
5. Atualize este README se necessário
