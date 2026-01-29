"""
Testes para validar a migração Ollama → Azure Foundry Local
"""

import sys
import logging
from llm_client import AzureFoundryLocalLLM
from schemas import ReportState, QueryResult
from prompts import build_queries
from config import setup_logging, validate_config

# Configurar logging
logger = setup_logging()


def test_connection() -> bool:
    """
    Teste 1: Verificar conexão com Foundry
    
    Returns:
        True se conexão bem-sucedida
    """
    print("\n🔌 Teste 1: Verificando conexão com Azure Foundry Local...")
    try:
        llm = AzureFoundryLocalLLM(model="Phi-4-mini-instruct-generic-gpu:5")
        print("✅ Conexão bem-sucedida!")
        return True
    except Exception as e:
        print(f"❌ Erro de conexão: {e}")
        logger.error(f"Erro de conexão: {e}")
        return False


def test_simple_invoke() -> bool:
    """
    Teste 2: Teste de invoke simples
    
    Returns:
        True se invoke bem-sucedido
    """
    print("\n📝 Teste 2: Testando invoke simples...")
    try:
        llm = AzureFoundryLocalLLM(model="Phi-4-mini-instruct-generic-gpu:5")
        response = llm.invoke("Olá! Qual é a capital da França? Responda em uma frase.")
        assert response.content, "Resposta vazia"
        print(f"✅ Resposta: {response.content[:100]}...")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro em test_simple_invoke: {e}")
        return False


def test_structured_output() -> bool:
    """
    Teste 3: Teste de structured output
    
    Returns:
        True se structured output bem-sucedido
    """
    print("\n📊 Teste 3: Testando structured output...")
    try:
        from pydantic import BaseModel
        from typing import List
        
        llm = AzureFoundryLocalLLM(model="Phi-4-mini-instruct-generic-gpu:5")
        
        class QueryList(BaseModel):
            queries: List[str]
        
        prompt = """
        Gere exatamente 3 queries de busca sobre o tema "machine learning".
        
        Responda APENAS em JSON válido, sem texto adicional:
        {
            "queries": ["query1", "query2", "query3"]
        }
        """
        
        structured_llm = llm.with_structured_output(QueryList)
        result = structured_llm.invoke(prompt)
        
        assert result.queries, "Lista de queries vazia"
        assert len(result.queries) > 0, "Nenhuma query gerada"
        print(f"✅ Queries geradas: {result.queries}")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro em test_structured_output: {e}")
        return False


def test_reasoning_model() -> bool:
    """
    Teste 4: Teste do modelo de raciocínio
    
    Returns:
        True se modelo de raciocínio funciona
    """
    print("\n🧠 Teste 4: Testando modelo de raciocínio (DeepSeek-R1)...")
    try:
        reasoning_llm = AzureFoundryLocalLLM(
            model="deepseek-r1-distill-qwen-7b-generic-gpu:3"
        )
        response = reasoning_llm.invoke("Qual é 5 + 3?")
        assert response.content, "Resposta vazia"
        print(f"✅ Resposta: {response.content[:150]}...")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro em test_reasoning_model: {e}")
        return False


def test_schemas() -> bool:
    """
    Teste 5: Validar schemas Pydantic
    
    Returns:
        True se schemas válidos
    """
    print("\n🏗️ Teste 5: Validando schemas...")
    try:
        # Testar QueryResult
        result = QueryResult(
            title="Test Title",
            url="https://example.com",
            resume="Test resume"
        )
        assert result.title == "Test Title"
        
        # Testar ReportState
        state = ReportState(
            user_input="Test question",
            queries=["query1", "query2"],
            queries_results=[result]
        )
        assert state.user_input == "Test question"
        assert len(state.queries) == 2
        
        print("✅ Schemas validados com sucesso")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro em test_schemas: {e}")
        return False


def test_config() -> bool:
    """
    Teste 6: Validar configuração centralizada
    
    Returns:
        True se configuração válida
    """
    print("\n⚙️ Teste 6: Validando configuração...")
    try:
        assert validate_config(), "Config validation falhou"
        
        from config import (
            LLM_MODEL, REASONING_MODEL, MAX_RAW_CHARS,
            FOUNDRY_ENDPOINT, TAVILY_MAX_RESULTS
        )
        
        assert LLM_MODEL, "LLM_MODEL vazio"
        assert REASONING_MODEL, "REASONING_MODEL vazio"
        assert MAX_RAW_CHARS > 0, "MAX_RAW_CHARS inválido"
        assert FOUNDRY_ENDPOINT, "FOUNDRY_ENDPOINT vazio"
        
        print("✅ Configuração válida")
        return True
    except Exception as e:
        print(f"❌ Erro: {e}")
        logger.error(f"Erro em test_config: {e}")
        return False


def main() -> int:
    """
    Executar todos os testes e retornar status
    
    Returns:
        0 se todos passam, 1 caso contrário
    """
    print("=" * 60)
    print("🚀 TESTES DE MIGRAÇÃO OLLAMA → AZURE FOUNDRY LOCAL")
    print("=" * 60)
    
    results = {
        "Conexão": test_connection(),
        "Invoke Simples": test_simple_invoke(),
        "Structured Output": test_structured_output(),
        "Modelo Raciocínio": test_reasoning_model(),
        "Schemas": test_schemas(),
        "Configuração": test_config(),
    }
    
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{test_name:.<40} {status}")
    
    print("=" * 60)
    print(f"Total: {passed}/{total} testes passaram")
    
    if passed == total:
        print("\n🎉 MIGRAÇÃO BEM-SUCEDIDA! Todos os testes passaram!")
        return 0
    else:
        print(f"\n⚠️ {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
    print("\n" + "=" * 60)
    print("📋 RESUMO DOS TESTES")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASSOU" if passed else "❌ FALHOU"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} testes passaram")
    
    if total_passed == total_tests:
        print("\n🎉 MIGRAÇÃO BEM-SUCEDIDA! Todos os testes passaram!")
        return 0
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
