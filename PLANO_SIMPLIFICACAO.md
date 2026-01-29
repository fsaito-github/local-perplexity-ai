# 🧹 Plano de Simplificação e Limpeza do Código

**Data:** 28 de janeiro de 2026  
**Status:** 📋 PLANEJAMENTO  
**Objetivo:** Simplificar, refatorar e melhorar a manutenibilidade do código

---

## 📊 Análise Atual do Projeto

### Estrutura de Arquivos
```
Local Perplexity AI/
├── perplexity.py ..................... 170 linhas (arquivo principal Streamlit)
├── llm_client.py ..................... 272 linhas (cliente Azure Foundry)
├── schemas.py ........................ 17 linhas (schemas Pydantic)
├── prompts.py ........................ 55 linhas (templates de prompts)
├── utils.py .......................... 235 linhas (funções de busca - POUCO USADO)
├── test_migration.py ................. 124 linhas (testes)
├── pyproject.toml .................... Dependências
├── README.md ......................... Documentação extensa
├── CHECKLIST.md ...................... Checklist de migração
├── MIGRATION_SUMMARY.md .............. Resumo de migração
└── plan.md ........................... Plano de migração (429 linhas)
```

### Problemas Identificados

#### 🔴 Críticos
1. **utils.py está subutilizado**: 235 linhas, mas apenas `TavilyClient` é usado
2. **Código morto**: Funções de busca nunca chamadas (`perplexity_search`, `openperplex_search`, `deduplicate_and_format_sources`)
3. **Documentação excessiva**: 3 arquivos de documentação redundantes
4. **llm_client.py complexo demais**: 272 linhas com lógica de retry repetida

#### 🟡 Médios
5. **Fallback manual em `build_first_queries()`**: Parsing manual de strings quando structured output falha
6. **Hardcoded `MAX_RAW_CHARS`**: Constante no meio do código principal
7. **Falta configuração centralizada**: Endpoints, timeouts, max_tokens espalhados
8. **Imports desnecessários**: Vários imports não utilizados
9. **Logging inconsistente**: Usa `print()` e `logger` misturados

#### 🟢 Menores
10. **Nomes de variáveis inconsistentes**: `llm_result`, `result`, `output`
11. **Comentários duplicados/óbvios**: Ex: "# Use o modelo base para síntese"
12. **Falta type hints completas**: Algumas funções sem tipos de retorno
13. **Tratamento de erros genérico**: `except Exception as e` muito genérico

---

## 🎯 Objetivos da Refatoração

### Princípios
- ✅ **Simplicidade**: Menos código, mais claro
- ✅ **Manutenibilidade**: Fácil de entender e modificar
- ✅ **Reutilização**: Componentes bem definidos
- ✅ **Testabilidade**: Código fácil de testar
- ✅ **Performance**: Sem otimizações prematuras

### Metas Específicas
- 📉 Reduzir linhas de código em ~30%
- 🗑️ Remover 100% do código morto
- 📝 Consolidar documentação em 1 arquivo
- ⚙️ Criar arquivo de configuração centralizado
- 🧪 Aumentar cobertura de testes

---

## 📋 Plano de Ação

### Fase 1: Limpeza de Código Morto (⏱️ 30 min)

#### 1.1 Remover Funções Não Utilizadas
**Arquivo: utils.py**
- ❌ Deletar `perplexity_search()` (155 linhas)
- ❌ Deletar `openperplex_search()` (23 linhas)
- ❌ Deletar `deduplicate_and_format_sources()` (55 linhas)
- ❌ Deletar `format_sources()` (11 linhas)
- ❌ Deletar `tavily_search()` (19 linhas) - usar direto de `TavilyClient`
- ✅ Manter apenas imports e decorators necessários

**Resultado esperado:** `utils.py` de 235 → 10 linhas (ou deletar completamente)

#### 1.2 Remover Imports Não Utilizados
**Arquivo: perplexity.py**
- ❌ `from pydantic import BaseModel` (não usado diretamente)
- ❌ `from langchain_openai import ChatOpenAI` (comentado)
- ❌ `from time import time` (não usado)
- ❌ `from langgraph.checkpoint.memory import MemorySaver` (não usado)

**Arquivo: utils.py**
- ❌ `import requests` (se deletar funções)
- ❌ `from openperplex import OpenperplexSync`
- ❌ `from typing import Dict, Any`

#### 1.3 Remover Código Comentado
**Arquivo: perplexity.py**
- ❌ Linha 17: `# llm = ChatOpenAI(model="gpt-4o")`
- ❌ Linha 141-145: Código comentado antigo

---

### Fase 2: Criar Arquivo de Configuração (⏱️ 20 min)

#### 2.1 Criar `config.py`
```python
"""Configuração centralizada do projeto"""
import os
from dotenv import load_dotenv

load_dotenv()

# Azure Foundry Settings
FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "http://127.0.0.1:52576")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "local")

# Modelos
LLM_MODEL = "Phi-4-mini-instruct-generic-gpu:5"
REASONING_MODEL = "deepseek-r1-distill-qwen-7b-generic-gpu:3"

# Parâmetros LLM
LLM_MAX_TOKENS = 512
LLM_TEMPERATURE = 0.7
LLM_STRUCTURED_TEMPERATURE = 0.3
LLM_TIMEOUT = 120
REASONING_TIMEOUT = 300

# Tavily Settings
TAVILY_MAX_RESULTS = 1
MAX_RAW_CHARS = 4000

# Streamlit
DEFAULT_QUERY = "How is the process of building a LLM?"
```

#### 2.2 Atualizar Imports
- `perplexity.py`: Importar constantes de `config.py`
- `llm_client.py`: Importar defaults de `config.py`
- `test_migration.py`: Importar configurações de `config.py`

---

### Fase 3: Simplificar `llm_client.py` (⏱️ 45 min)

#### 3.1 Refatorar Lógica de Retry
**Problema atual:** 80+ linhas de código duplicado para retry

**Solução:** Extrair função auxiliar
```python
def _make_request_with_retry(url, payload, headers, timeout, max_retries=2):
    """Fazer requisição HTTP com retry automático"""
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Tentativa {attempt+1} falhou, tentando novamente...")
```

**Resultado esperado:** `llm_client.py` de 272 → 180 linhas (~33% redução)

#### 3.2 Simplificar Parsing de JSON
**Problema atual:** 3 níveis de fallback para parsear JSON

**Solução:** Função auxiliar única
```python
def _extract_and_parse_json(content: str, schema: Type[T]) -> Optional[T]:
    """Tentar extrair e parsear JSON de resposta LLM"""
    # Tentativa 1: Regex {...}
    # Tentativa 2: Parse direto
    # Retorna None se falhar
```

#### 3.3 Remover Logging Excessivo
- Manter apenas logs de erro (ERROR/WARNING)
- Remover logs DEBUG desnecessários
- Consolidar mensagens de erro

---

### Fase 4: Refatorar `perplexity.py` (⏱️ 1 hora)

#### 4.1 Simplificar `build_first_queries()`
**Problema:** Fallback manual complexo (25 linhas)

**Solução 1:** Usar apenas structured output, sem fallback
```python
def build_first_queries(state: ReportState):
    class QueryList(BaseModel):
        queries: List[str]
    
    prompt = build_queries.format(user_input=state.user_input)
    query_llm = llm.with_structured_output(QueryList)
    result = query_llm.invoke(prompt)
    return {"queries": result.queries}
```

**Solução 2 (se precisar fallback):** Mover lógica para `llm_client.py`

**Resultado esperado:** 40 → 10 linhas (75% redução)

#### 4.2 Extrair Função de Formatação
**Problema:** Lógica de formatação misturada em `final_writer()`

**Solução:** Criar funções auxiliares
```python
def _format_search_results(queries_results: List[QueryResult]) -> str:
    """Formatar resultados para o prompt"""
    # ...

def _format_references(queries_results: List[QueryResult]) -> str:
    """Formatar referências para output"""
    # ...

def final_writer(state: ReportState):
    search_results = _format_search_results(state.queries_results)
    references = _format_references(state.queries_results)
    
    prompt = build_final_response.format(
        user_input=state.user_input,
        search_results=search_results
    )
    
    response = llm.invoke(prompt)
    return {"final_response": f"{response.content}\n\nReferences:\n{references}"}
```

#### 4.3 Simplificar `single_search()`
**Antes:** 24 linhas
```python
def single_search(query: str):
    tavily_client = TavilyClient()
    results = tavily_client.search(query, max_results=1, include_raw_content=False)
    
    query_results = []
    for result in results["results"]:
        url = result["url"]
        url_extraction = tavily_client.extract(url)
        
        if len(url_extraction["results"]) > 0:
            raw_content = url_extraction["results"][0]["raw_content"]
            if raw_content:
                raw_content = raw_content[:MAX_RAW_CHARS]
            
            prompt = resume_search.format(
                user_input=query,
                search_results=raw_content
            )
            
            llm_result = llm.invoke(prompt)
            query_results.append(QueryResult(
                title=result["title"],
                url=url,
                resume=llm_result.content
            ))
    
    return {"queries_results": query_results}
```

**Depois:** 12 linhas
```python
def single_search(query: str):
    from config import MAX_RAW_CHARS, TAVILY_MAX_RESULTS
    
    tavily = TavilyClient()
    results = tavily.search(query, max_results=TAVILY_MAX_RESULTS)
    
    query_results = []
    for result in results["results"]:
        content = _extract_content(tavily, result["url"], MAX_RAW_CHARS)
        if content:
            resume = _summarize_content(query, content)
            query_results.append(QueryResult(
                title=result["title"],
                url=result["url"],
                resume=resume
            ))
    
    return {"queries_results": query_results}

def _extract_content(tavily, url: str, max_chars: int) -> Optional[str]:
    """Extrair e truncar conteúdo de URL"""
    extraction = tavily.extract(url)
    if extraction["results"]:
        content = extraction["results"][0].get("raw_content", "")
        return content[:max_chars] if content else None
    return None

def _summarize_content(query: str, content: str) -> str:
    """Resumir conteúdo usando LLM"""
    prompt = resume_search.format(user_input=query, search_results=content)
    return llm.invoke(prompt).content
```

#### 4.4 Melhorar Interface Streamlit
**Melhorias:**
- Adicionar spinner durante processamento
- Mostrar progresso das etapas
- Melhor formatação de erros
- Adicionar cache para queries recentes

---

### Fase 5: Melhorar Type Hints e Documentação (⏱️ 30 min)

#### 5.1 Adicionar Type Hints Completos
**Arquivos a atualizar:**
- `perplexity.py`: Todas as funções
- `llm_client.py`: Parâmetros opcionais
- `schemas.py`: Adicionar validadores Pydantic

#### 5.2 Adicionar Docstrings Consistentes
**Formato Google Style:**
```python
def single_search(query: str) -> dict[str, List[QueryResult]]:
    """Executar busca e resumir resultado.
    
    Args:
        query: Query de busca
        
    Returns:
        Dict com lista de QueryResult
        
    Raises:
        ValueError: Se a busca falhar
    """
```

---

### Fase 6: Consolidar Documentação (⏱️ 30 min)

#### 6.1 Arquivos a Deletar/Mesclar
- ❌ **Deletar:** `CHECKLIST.md` (234 linhas) - tarefa concluída
- ❌ **Deletar:** `MIGRATION_SUMMARY.md` (206 linhas) - histórico
- ❌ **Deletar:** `plan.md` (429 linhas) - plano antigo
- ✅ **Manter:** `README.md` (simplificado)
- ✅ **Manter:** `PLANO_SIMPLIFICACAO.md` (este arquivo)

#### 6.2 Reestruturar README.md
**Nova estrutura (100 linhas):**
```markdown
# 🌎 Local Perplexity AI

Clone local do Perplexity usando Azure AI Foundry Local + LangGraph

## 🚀 Quick Start
## 📦 Instalação
## ⚙️ Configuração
## 💻 Uso
## 🏗️ Arquitetura
## 🧪 Testes
## 🔧 Troubleshooting
## 📝 Licença
```

---

### Fase 7: Melhorar Testes (⏱️ 45 min)

#### 7.1 Adicionar Mais Testes
**Arquivo: test_migration.py**
- ✅ Testes unitários para funções auxiliares
- ✅ Testes de integração do grafo LangGraph
- ✅ Testes de erro (casos negativos)
- ✅ Mocks para chamadas externas

#### 7.2 Adicionar Coverage
```bash
pytest --cov=. --cov-report=html
```

#### 7.3 Configurar CI/CD (Opcional)
- GitHub Actions para rodar testes
- Linting automático (ruff, black)
- Type checking (mypy)

---

### Fase 8: Adicionar Logging Estruturado (⏱️ 30 min)

#### 8.1 Configurar Logging Centralizado
**Arquivo: config.py**
```python
import logging
import sys

def setup_logging(level=logging.INFO):
    """Configurar logging estruturado"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('perplexity.log')
        ]
    )
```

#### 8.2 Substituir `print()` por `logger`
- `perplexity.py`: Substituir todos os `print()`
- `llm_client.py`: Já usa logger (manter)
- `test_migration.py`: Manter print (é para exibição)

---

## 📊 Resumo das Melhorias

### Antes vs Depois

| Métrica | Antes | Depois | Redução |
|---------|-------|--------|---------|
| **Total de Linhas** | ~1,500 | ~900 | 40% |
| **perplexity.py** | 170 | 120 | 29% |
| **llm_client.py** | 272 | 180 | 34% |
| **utils.py** | 235 | DELETADO | 100% |
| **Documentação** | 869 | 100 | 88% |
| **Código Morto** | ~200 linhas | 0 | 100% |
| **Funções com Type Hints** | 60% | 100% | +40% |
| **Cobertura de Testes** | 40% | 80% | +40% |

### Benefícios

#### 🎯 Imediatos
- ✅ Código mais fácil de entender
- ✅ Menos bugs potenciais
- ✅ Documentação clara e concisa
- ✅ Configuração centralizada

#### 🚀 Médio Prazo
- ✅ Facilidade de adicionar features
- ✅ Onboarding mais rápido
- ✅ Manutenção simplificada
- ✅ Testes mais robustos

#### 💎 Longo Prazo
- ✅ Código sustentável
- ✅ Escalabilidade
- ✅ Reutilização de componentes
- ✅ Menor dívida técnica

---

## 🗓️ Cronograma de Execução

### Semana 1: Limpeza e Organização
- **Dia 1:** Fase 1 - Limpeza de Código Morto
- **Dia 2:** Fase 2 - Arquivo de Configuração
- **Dia 3:** Fase 6 - Consolidar Documentação

### Semana 2: Refatoração Core
- **Dia 4-5:** Fase 3 - Simplificar `llm_client.py`
- **Dia 6-8:** Fase 4 - Refatorar `perplexity.py`

### Semana 3: Qualidade e Testes
- **Dia 9-10:** Fase 5 - Type Hints e Documentação
- **Dia 11-12:** Fase 7 - Melhorar Testes
- **Dia 13:** Fase 8 - Logging Estruturado

### Validação Final
- **Dia 14:** Testes E2E completos
- **Dia 15:** Revisão de código e ajustes finais

---

## ⚠️ Riscos e Mitigação

### Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| Quebrar funcionalidade existente | Média | Alto | Testes abrangentes antes de cada fase |
| Dependências quebradas | Baixa | Médio | Documentar versões exatas |
| Performance degradada | Baixa | Médio | Benchmarks antes/depois |
| Conflitos de merge | Baixa | Baixo | Branch separado para refatoração |

### Estratégia de Rollback
- ✅ Git branch separado: `feature/simplificacao`
- ✅ Commits atômicos por fase
- ✅ Tags antes de mudanças grandes
- ✅ Backup do código atual

---

## ✅ Checklist de Aceitação

### Critérios de Sucesso
- [ ] Todos os testes passam (100%)
- [ ] Cobertura de testes > 80%
- [ ] Redução de ~40% no total de linhas
- [ ] Zero código morto
- [ ] Zero imports não utilizados
- [ ] 100% das funções com type hints
- [ ] 100% das funções públicas com docstrings
- [ ] Documentação consolidada em 1 arquivo
- [ ] Aplicação funciona igual ou melhor que antes
- [ ] Performance igual ou superior
- [ ] Código passa em linter (ruff/black)
- [ ] Código passa em type checker (mypy)

### Validação de Qualidade
```bash
# Linting
ruff check .

# Formatting
black --check .

# Type checking
mypy perplexity.py llm_client.py

# Testes
pytest -v --cov=.

# Funcionalidade
streamlit run perplexity.py
```

---

## 📚 Referências

- [Clean Code - Robert Martin](https://www.amazon.com/Clean-Code-Handbook-Software-Craftsmanship/dp/0132350882)
- [Python Best Practices](https://docs.python-guide.org/)
- [LangGraph Best Practices](https://python.langchain.com/docs/langgraph)
- [Pydantic Documentation](https://docs.pydantic.dev/)

---

## 🎯 Próximos Passos

1. **Revisar plano com equipe** ✋
2. **Aprovação para iniciar** ✋
3. **Criar branch `feature/simplificacao`** ✋
4. **Executar Fase 1** ⏳
5. **Validar e iterar** ⏳

---

**Última atualização:** 28 de janeiro de 2026  
**Autor:** GitHub Copilot  
**Status:** ✅ PLANO COMPLETO - AGUARDANDO APROVAÇÃO
