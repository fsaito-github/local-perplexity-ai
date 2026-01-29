# 📚 ÍNDICE DE DOCUMENTAÇÃO

> Guia de navegação pela documentação do projeto Local Perplexity AI

---

## 🚀 COMEÇANDO

**Para Usuários Finais:**
1. Leia [README.md](README.md) - 5 minutos
2. Siga "Quick Start" para instalar e rodar
3. Teste a aplicação em http://localhost:8501

**Para Desenvolvedores:**
1. Leia [README.md](README.md) para entender o projeto
2. Leia [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) para ver mudanças
3. Explore [config.py](config.py) para entender configurações
4. Examine docstrings no código com `help(funcao)`

---

## 📖 DOCUMENTAÇÃO POR TÓPICO

### Visão Geral
| Arquivo | Conteúdo | Leitor Ideal |
|---------|----------|--------------|
| [README.md](README.md) | Guia principal, quick start | Todos |
| [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) | Resumo de mudanças | Dev |
| [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) | Detalhes da refatoração | Dev |

### Técnico
| Arquivo | Conteúdo | Leitor Ideal |
|---------|----------|--------------|
| [config.py](config.py) | Configuração centralizada | Dev |
| [perplexity.py](perplexity.py) | App principal + LangGraph | Dev |
| [llm_client.py](llm_client.py) | Cliente Azure Foundry | Dev |
| [schemas.py](schemas.py) | Modelos Pydantic | Dev |
| [prompts.py](prompts.py) | Templates de prompts | Dev/PM |

### Histórico
| Arquivo | Conteúdo | Propósito |
|---------|----------|-----------|
| [PLANO_SIMPLIFICACAO.md](PLANO_SIMPLIFICACAO.md) | Plano original | Referência |
| [README_OLD.md](README_OLD.md) | README antigo | Histórico |

---

## 🔍 ENCONTRAR INFORMAÇÕES

### "Como inicio a aplicação?"
→ [README.md](README.md) - Seção "Execução"

### "Como configuro parâmetros?"
→ [config.py](config.py) ou [README.md](README.md) - Seção "⚙️ Configuração"

### "O que mudou na refatoração?"
→ [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

### "Como adiciono um novo tipo de busca?"
→ [perplexity.py](perplexity.py) - Função `single_search()`
→ [llm_client.py](llm_client.py) - Classe `AzureFoundryLocalLLM`

### "Como faço debug?"
→ Verifique `perplexity.log`
→ Aumente `LOG_LEVEL` em [config.py](config.py)

### "Como rodo os testes?"
→ `python test_migration.py`
→ Veja [README.md](README.md) - Seção "🧪 Testes"

### "O que é cada arquivo?"
→ Veja "Estrutura de Arquivos" neste documento

---

## 📂 ESTRUTURA DE ARQUIVOS

### Arquivos de Código

**[perplexity.py](perplexity.py)** (188 linhas)
- Aplicação Streamlit principal
- Grafo LangGraph com 4 nós
- Funções auxiliares para formatação
- Entry point: `streamlit run perplexity.py`

**[config.py](config.py)** (80 linhas) ✨ NOVO
- Configuração centralizada
- Setup de logging
- Validação de configuração
- Importar daqui para customizar

**[llm_client.py](llm_client.py)** (190 linhas)
- Cliente para Azure Foundry Local
- Métodos: invoke() e invoke_structured()
- Funções auxiliares para requests HTTP
- Compatível com LangChain

**[schemas.py](schemas.py)** (30 linhas)
- Modelos Pydantic: QueryResult, ReportState
- Tipagem forte para o projeto
- Validação automática

**[prompts.py](prompts.py)** (45 linhas)
- Templates de prompts LLM
- 3 prompts: build_queries, resume_search, build_final_response
- Fácil de customizar

**[utils.py](utils.py)** (3 linhas)
- Apenas TavilyClient importado
- Funções mortas removidas
- Mantém compatibilidade

**[test_migration.py](test_migration.py)** (193 linhas)
- Suite de testes: 6 testes
- Valida: conexão, invoke, structured, reasoning, schemas, config
- Pode rodar independentemente

### Arquivos de Documentação

**[README.md](README.md)** (203 linhas)
- Documentação consolidada
- Quick start
- Arquitetura
- Troubleshooting
- **COMECE AQUI**

**[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** (250+ linhas)
- Sumário executivo da refatoração
- O que mudou
- Métricas de qualidade
- Como usar agora

**[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** (300+ linhas)
- Detalhes completos da refatoração
- 8 fases documentadas
- Destaques de código
- Aprendizados

**[PLANO_SIMPLIFICACAO.md](PLANO_SIMPLIFICACAO.md)** (400+ linhas)
- Plano original detalhado
- Análise de problemas
- Objetivos e metas
- **Referência histórica**

**[README_OLD.md](README_OLD.md)**
- README original
- **Referência histórica**

### Arquivos de Configuração

**[pyproject.toml](pyproject.toml)**
- Dependências Poetry
- Versões de pacotes

**[.env](.)** (variáveis de ambiente)
```
FOUNDRY_ENDPOINT=http://127.0.0.1:52576
FOUNDRY_API_KEY=local
```

**[start_foundry.bat](start_foundry.bat)**
- Script Windows para iniciar Foundry
- Executar em Terminal do Windows

### Arquivos Gerados

**[perplexity.log](.)** (auto-gerado)
- Log de execução
- Criado automaticamente ao rodar a app

---

## 🎯 GUIAS POR TAREFA

### Tarefa: "Iniciar a aplicação"
```
1. Abra Terminal 1
2. Execute: start_foundry.bat
3. Aguarde "Server started"
4. Abra Terminal 2
5. Execute: streamlit run perplexity.py
6. Acesse: http://localhost:8501
```
Documentação: [README.md](README.md) - "🚀 Quick Start"

### Tarefa: "Configurar parâmetros"
```
1. Abra config.py
2. Edite constantes (ex: LLM_MAX_TOKENS = 1024)
3. Salve arquivo
4. Reinicie a aplicação
```
Documentação: [config.py](config.py)

### Tarefa: "Adicionar tipo de busca"
```
1. Edite single_search() em perplexity.py
2. Adicione lógica para novo tipo
3. Adicione teste em test_migration.py
4. Rode: python test_migration.py
```
Documentação: [perplexity.py](perplexity.py)

### Tarefa: "Debug de erro"
```
1. Verifique perplexity.log
2. Aumente LOG_LEVEL em config.py
3. Reinicie aplicação
4. Veja logs detalhados
```
Documentação: [config.py](config.py) - setup_logging()

### Tarefa: "Entender fluxo"
```
1. Leia [README.md](README.md) - "Fluxo de Execução"
2. Veja diagrama de nós
3. Examine funções em perplexity.py
4. Trace código com debugger
```
Documentação: [README.md](README.md), [perplexity.py](perplexity.py)

### Tarefa: "Customizar prompts"
```
1. Abra prompts.py
2. Edite templates (build_queries, etc)
3. Teste com: python test_migration.py
```
Documentação: [prompts.py](prompts.py)

---

## 🔗 RELACIONAMENTOS ENTRE ARQUIVOS

```
README.md (mapa)
  ├─> config.py (configuração)
  ├─> perplexity.py (aplicação)
  │   ├─> config.py
  │   ├─> llm_client.py
  │   ├─> schemas.py
  │   ├─> prompts.py
  │   └─> utils.py
  └─> test_migration.py (testes)
      ├─> config.py
      ├─> llm_client.py
      ├─> schemas.py
      └─> prompts.py

IMPLEMENTATION_COMPLETE.md (resumo)
  └─> REFACTORING_SUMMARY.md (detalhes)
      └─> PLANO_SIMPLIFICACAO.md (história)
```

---

## 🎓 LEARN MORE

### Conceitos
- **LangGraph:** Grafo de tarefas paralelas
- **Pydantic:** Validação de tipos em Python
- **Streamlit:** Framework web minimalista
- **Azure Foundry:** LLM local offline

### Documentações Externas
- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [Pydantic Docs](https://docs.pydantic.dev/)
- [Streamlit Docs](https://docs.streamlit.io)
- [Azure AI Foundry](https://azure.microsoft.com/en-us/products/ai-services/ai-foundry)

---

## ❓ FAQ

**P: Qual arquivo modificar para customizar?**
R: [config.py](config.py) para constantes e logging, [prompts.py](prompts.py) para mensagens

**P: Onde está o log?**
R: `perplexity.log` (criado automaticamente)

**P: Como rodar testes?**
R: `python test_migration.py`

**P: Qual é a versão?**
R: v2.0 (pós-refatoração) - veja [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)

**P: Pode usar em produção?**
R: Sim! Verifique [README.md](README.md) - "Status: Pronto para Produção"

**P: Como reportar bugs?**
R: Verifique `perplexity.log` primeiro, depois consulte [README.md](README.md) - Troubleshooting

---

## 📞 SUPORTE RÁPIDO

| Problema | Solução | Documentação |
|----------|---------|--------------|
| Conexão recusada | Rodou `start_foundry.bat`? | [README.md](README.md) |
| Timeout | Aumentar timeout em [config.py](config.py) | [config.py](config.py) |
| Erro de sintaxe | Verifique perplexity.log | [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) |
| Teste falha | Rodou `python test_migration.py` | [README.md](README.md) |

---

## 📊 ESTATÍSTICAS

- **Total de Documentação:** 4 arquivos, ~1,200 linhas
- **Código Documentado:** 100% (type hints + docstrings)
- **Cobertura de Guias:** Todas as principais tarefas
- **Última Atualização:** 28 de janeiro de 2026

---

## 🎯 RESUMO

**Use este arquivo para navegar:**
1. Iniciante? → [README.md](README.md)
2. Dev novo? → [README.md](README.md) + [config.py](config.py)
3. Entender mudanças? → [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)
4. Deep dive? → [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)
5. Histórico? → [PLANO_SIMPLIFICACAO.md](PLANO_SIMPLIFICACAO.md)

---

**Versão:** 2.0  
**Status:** ✅ Completo  
**Data:** 28 de janeiro de 2026
