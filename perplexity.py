from pydantic import BaseModel
from llm_client import AzureFoundryLocalLLM
from langgraph.graph import START, END, StateGraph
from langgraph.types import Send
import streamlit as st
from typing import Optional

from config import (
    LLM_MODEL, LLM_MAX_TOKENS, LLM_TIMEOUT,
    REASONING_MODEL, REASONING_MAX_TOKENS, REASONING_TIMEOUT,
    MAX_RAW_CHARS, MAX_VERIFICATION_RETRIES,
    STREAMLIT_TITLE, DEFAULT_QUERY,
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

def build_first_queries(state: ReportState) -> dict:
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
    Suporta retry com feedback do verificador.
    
    Args:
        state: Estado da aplicação
        
    Returns:
        Dict com resposta final e referências
    """
    search_results = _format_search_results(state.queries_results)
    references = _format_references(state.queries_results)
    
    feedback_section = ""
    if state.verification_feedback:
        feedback_section = (
            f"\n\nIMPORTANT - A previous version of your response was rejected by a verification agent. "
            f"Please fix the following issues:\n{state.verification_feedback}\n"
            f"Rewrite the response ensuring ALL claims are directly supported by the search results."
        )
    
    prompt = build_final_response.format(
        user_input=state.user_input,
        search_results=search_results,
        verification_feedback=feedback_section
    )
    
    response = reasoning_llm.invoke(prompt)
    final_response = f"{response.content}\n\nReferences:\n{references}"
    
    retry_info = f" (attempt {state.retry_count + 1})" if state.retry_count > 0 else ""
    logger.info(f"✅ Final response generated{retry_info}: {len(response.content)} chars")
    
    return {"final_response": final_response}


def verify_response(state: ReportState) -> dict:
    """
    Verificar se a resposta final contém apenas informações suportadas pelas fontes.
    
    Args:
        state: Estado da aplicação
        
    Returns:
        Dict com resultado da verificação e feedback se necessário
    """
    search_results = _format_search_results(state.queries_results)
    
    # Extrair apenas o conteúdo da resposta (sem a seção References)
    response_text = state.final_response
    if "\n\nReferences:\n" in response_text:
        response_text = response_text.split("\n\nReferences:\n")[0]
    
    prompt = verify_response_prompt.format(
        final_response=response_text,
        search_results=search_results
    )
    
    try:
        verification_llm = reasoning_llm.with_structured_output(VerificationResult)
        result = verification_llm.invoke(prompt)
        
        if result.is_valid:
            logger.info("✅ Verification passed - response is supported by sources")
            return {"verification_feedback": None}
        else:
            supported = sum(1 for c in result.claims if c.is_supported)
            total = len(result.claims)
            logger.warning(
                f"⚠️ Verification failed - {supported}/{total} claims supported. "
                f"Retry {state.retry_count + 1}/{MAX_VERIFICATION_RETRIES}"
            )
            return {
                "verification_feedback": result.feedback,
                "retry_count": state.retry_count + 1
            }
    except Exception as e:
        logger.error(f"Erro na verificação: {e}. Aceitando resposta sem verificação.")
        return {"verification_feedback": None}


def should_retry(state: ReportState) -> str:
    """
    Decidir se deve regenerar a resposta ou finalizar.
    
    Returns:
        'final_writer' para regenerar, 'end' para finalizar
    """
    if state.verification_feedback is None:
        return "end"
    if state.retry_count >= MAX_VERIFICATION_RETRIES:
        logger.warning(f"⚠️ Max retries ({MAX_VERIFICATION_RETRIES}) reached. Accepting response with issues.")
        return "end"
    return "final_writer"


builder = StateGraph(ReportState)
builder.add_node("build_first_queries", build_first_queries)
builder.add_node("single_search", single_search)
builder.add_node("final_writer", final_writer)
builder.add_node("verify_response", verify_response)

builder.add_edge(START, "build_first_queries")
builder.add_conditional_edges("build_first_queries", 
                              spawn_researchers, 
                              ["single_search"])
builder.add_edge("single_search", "final_writer")
builder.add_edge("final_writer", "verify_response")
builder.add_conditional_edges(
    "verify_response",
    should_retry,
    {"final_writer": "final_writer", "end": END}
)

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
                    
                    retry_count = output.get("retry_count", 0)
                    verification_feedback = output.get("verification_feedback")
                    
                    if retry_count >= MAX_VERIFICATION_RETRIES and verification_feedback:
                        st.warning(
                            f"⚠️ Response accepted after {retry_count} verification attempts. "
                            f"Some claims may not be fully supported by sources."
                        )
                    else:
                        st.success("✅ Response generated and verified!")
                    
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
