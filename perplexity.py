from pydantic import BaseModel
from llm_client import AzureFoundryLocalLLM
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
import streamlit as st
from typing import Optional

from config import (
    LLM_MODEL, LLM_MAX_TOKENS, LLM_TIMEOUT,
    REASONING_MODEL, REASONING_MAX_TOKENS, REASONING_TIMEOUT,
    MAX_RAW_CHARS, STREAMLIT_TITLE, DEFAULT_QUERY,
    setup_logging, validate_config
)
from schemas import *
from prompts import *
from utils import TavilyClient

from dotenv import load_dotenv
load_dotenv()

# Configurar logging
logger = setup_logging()

# Validar configuração
validate_config()

# Modelos Azure AI Foundry Local
llm = AzureFoundryLocalLLM(
    model=LLM_MODEL,
    max_tokens=LLM_MAX_TOKENS,
    timeout=LLM_TIMEOUT
)
reasoning_llm = AzureFoundryLocalLLM(
    model=REASONING_MODEL,
    max_tokens=REASONING_MAX_TOKENS,
    timeout=REASONING_TIMEOUT
)


# ============================================================================
# FUNÇÕES AUXILIARES
# ============================================================================

def _extract_url_content(tavily: TavilyClient, url: str, max_chars: int) -> str | None:
    """
    Extrair e truncar conteúdo de URL usando Tavily.
    
    Args:
        tavily: Cliente Tavily
        url: URL para extrair
        max_chars: Máximo de caracteres a retornar
        
    Returns:
        Conteúdo truncado ou None se não conseguir extrair
    """
    try:
        extraction = tavily.extract(url)
        if extraction.get("results"):
            content = extraction["results"][0].get("raw_content", "")
            return content[:max_chars] if content else None
    except Exception as e:
        logger.warning(f"Erro ao extrair conteúdo de {url}: {e}")
    return None


def _summarize_content(query: str, content: str) -> str:
    """
    Resumir conteúdo usando LLM.
    
    Args:
        query: Query original
        content: Conteúdo a resumir
        
    Returns:
        Resumo do conteúdo
    """
    prompt = resume_search.format(user_input=query, search_results=content)
    response = llm.invoke(prompt)
    return response.content


def _format_search_results(queries_results: list[QueryResult]) -> str:
    """
    Formatar resultados de busca para prompt.
    
    Args:
        queries_results: Lista de resultados de busca
        
    Returns:
        String formatada com os resultados
    """
    formatted = ""
    for i, result in enumerate(queries_results, 1):
        formatted += f"[{i}]\n\n"
        formatted += f"Title: {result.title}\n"
        formatted += f"URL: {result.url}\n"
        formatted += f"Content: {result.resume}\n"
        formatted += "================\n\n"
    return formatted


def _format_references(queries_results: list[QueryResult]) -> str:
    """
    Formatar referências para output.
    
    Args:
        queries_results: Lista de resultados de busca
        
    Returns:
        String com referências formatadas
    """
    return "\n".join(
        f"[{i}] - [{result.title}]({result.url})"
        for i, result in enumerate(queries_results, 1)
    )


# ============================================================================
# NÓS DO GRAFO LANGGRAPH
# ============================================================================ 
    """
    Gerar lista de queries de busca a partir da pergunta do usuário.
    
    Args:
        state: Estado da aplicação contendo user_input
        
    Returns:
        Dict com lista de queries
    """
    class QueryList(BaseModel):
        queries: list[str]
        
    user_input = state.user_input
    prompt = build_queries.format(user_input=user_input)
    
    try:
        query_llm = llm.with_structured_output(QueryList)
        result = query_llm.invoke(prompt)
        return {"queries": result.queries}
    except Exception as e:
        logger.error(f"Erro ao gerar queries estruturado: {e}")
        raise

def spawn_researchers(state: ReportState) -> list[Send]:
    """
    Criar tarefas de busca paralelas para cada query.
    
    Args:
        state: Estado contendo lista de queries
        
    Returns:
        Lista de Send objects para execução paralela
    """
    return [Send("single_search", query) for query in state.queries]

def single_search(query: str) -> dict[str, list[QueryResult]]:
    """
    Executar busca web e resumir resultado.
    
    Args:
        query: Query de busca
        
    Returns:
        Dict com lista de QueryResult
    """
    tavily = TavilyClient()
    results = tavily.search(query, max_results=1, include_raw_content=False)
    
    query_results = []
    for result in results["results"]:
        url = result["url"]
        content = _extract_url_content(tavily, url, MAX_RAW_CHARS)
        
        if content:
            resume = _summarize_content(query, content)
            query_results.append(QueryResult(
                title=result["title"],
                url=url,
                resume=resume
            ))
    
    return {"queries_results": query_results}
    

def final_writer(state: ReportState) -> dict[str, str]:
    """
    Gerar resposta final usando LLM com base nos resultados de busca.
    
    Args:
        state: Estado da aplicação
        
    Returns:
        Dict com resposta final e referências
    """
    search_results = _format_search_results(state.queries_results)
    references = _format_references(state.queries_results)
    
    prompt = build_final_response.format(
        user_input=state.user_input,
        search_results=search_results
    )
    
    response = reasoning_llm.invoke(prompt)
    final_response = f"{response.content}\n\nReferences:\n{references}"
    
    logger.info(f"✅ Final response generated: {len(response.content)} chars")
    
    return {"final_response": final_response}


builder = StateGraph(ReportState)
builder.add_node("build_first_queries", build_first_queries)
builder.add_node("single_search", single_search)
builder.add_node("final_writer", final_writer)

builder.add_edge(START, "build_first_queries")
builder.add_conditional_edges("build_first_queries", 
                              spawn_researchers, 
                              ["single_search"])
builder.add_edge("single_search", "final_writer")
builder.add_edge("final_writer", END) 

graph = builder.compile()



if __name__ == "__main__":
    st.title(STREAMLIT_TITLE)
    user_input = st.text_input("What's your question?", 
                               value=DEFAULT_QUERY)

    if st.button("Search"):
        with st.status("Generating response", expanded=True):
            try:
                logger.info(f"Iniciando busca para: {user_input}")
                output = graph.invoke({"user_input": user_input})
                
                if "final_response" in output:
                    final_response = output["final_response"]
                    st.success("✅ Response generated successfully!")
                    st.markdown(final_response)
                    logger.info("✅ Response generated successfully")
                else:
                    st.error("❌ Response does not contain 'final_response'")
                    st.write(output)
                    logger.error("Response does not contain 'final_response'")
            except Exception as e:
                st.error(f"❌ Error generating response: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
                logger.error(f"Error generating response: {str(e)}", exc_info=True)
