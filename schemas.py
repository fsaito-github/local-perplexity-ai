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


class VerificationClaim(BaseModel):
    """Resultado da verificação de uma afirmação individual.
    
    Attributes:
        claim: A afirmação extraída da resposta
        citation_number: Número da citação usada [N]
        is_supported: Se a fonte realmente suporta a afirmação
        reason: Explicação de por que sim/não
    """
    claim: str = Field(..., description="Afirmação extraída da resposta")
    citation_number: int = Field(..., description="Número da citação [N]")
    is_supported: bool = Field(..., description="Se a fonte suporta a afirmação")
    reason: str = Field(..., description="Explicação da verificação")


class VerificationResult(BaseModel):
    """Resultado agregado da verificação da resposta.
    
    Attributes:
        claims: Lista de afirmações verificadas
        is_valid: True se todas as claims são suportadas
        feedback: Resumo dos problemas encontrados (para retry)
    """
    claims: List[VerificationClaim] = Field(default_factory=list, description="Claims verificadas")
    is_valid: bool = Field(False, description="Se a resposta é válida")
    feedback: str = Field("", description="Feedback para correção")


class ReportState(BaseModel):
    """Estado do grafo LangGraph da aplicação.
    
    Attributes:
        user_input: Pergunta do usuário
        queries: Lista de queries geradas
        queries_results: Resultados das buscas acumulados
        final_response: Resposta final gerada
        verification_feedback: Feedback do verificador para retry
        retry_count: Número de tentativas de regeneração
    """
    user_input: Optional[str] = Field(None, description="Pergunta do usuário")
    final_response: Optional[str] = Field(None, description="Resposta final")
    queries: List[str] = Field(default_factory=list, description="Queries geradas")
    queries_results: Annotated[List[QueryResult], operator.add] = Field(
        default_factory=list,
        description="Resultados acumulados das buscas"
    )
    verification_feedback: Optional[str] = Field(None, description="Feedback do verificador")
    retry_count: int = Field(0, description="Contador de tentativas de regeneração")


__all__ = ["QueryResult", "VerificationClaim", "VerificationResult", "ReportState"]




