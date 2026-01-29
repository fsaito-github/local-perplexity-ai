"""Schemas Pydantic para o projeto Local Perplexity"""

import operator
from typing import Annotated, List, Optional
from pydantic import BaseModel, Field


class QueryResult(BaseModel):
    """Resultado de uma busca web com resumo do conteúdo.
    
    Attributes:
        title: Título do resultado de busca
        url: URL do resultado
        resume: Resumo do conteúdo da página
    """
    title: Optional[str] = Field(None, description="Título do resultado")
    url: Optional[str] = Field(None, description="URL do resultado")
    resume: Optional[str] = Field(None, description="Resumo do conteúdo")


class ReportState(BaseModel):
    """Estado do grafo LangGraph da aplicação.
    
    Attributes:
        user_input: Pergunta do usuário
        queries: Lista de queries geradas
        queries_results: Resultados das buscas acumulados
        final_response: Resposta final gerada
    """
    user_input: Optional[str] = Field(None, description="Pergunta do usuário")
    final_response: Optional[str] = Field(None, description="Resposta final")
    queries: List[str] = Field(default_factory=list, description="Queries geradas")
    queries_results: Annotated[List[QueryResult], operator.add] = Field(
        default_factory=list,
        description="Resultados acumulados das buscas"
    )


__all__ = ["QueryResult", "ReportState"]




