"""
Azure AI Foundry Local LLM Client
Wrapper para compatibilidade com LangChain
"""

from pydantic import BaseModel
from typing import Type, TypeVar, Optional
import json
import re
import logging
import requests
import os

# Importar configuração
try:
    from config import FOUNDRY_ENDPOINT, FOUNDRY_API_KEY
except ImportError:
    FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "http://127.0.0.1:52576")
    FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "local")

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)


def _make_request(url: str, payload: dict, headers: dict, timeout: int) -> dict:
    """
    Fazer requisição HTTP ao API do Foundry.
    
    Args:
        url: URL do endpoint
        payload: Payload JSON
        headers: Headers HTTP
        timeout: Timeout em segundos
        
    Returns:
        Response JSON parseado
        
    Raises:
        requests.HTTPError: Se a requisição falhar
    """
    response = requests.post(url, json=payload, headers=headers, timeout=timeout)
    
    if not response.ok:
        logger.error(f"HTTP {response.status_code}: {response.text[:500]}")
    
    response.raise_for_status()
    return response.json()


def _extract_json(content: str) -> Optional[dict]:
    """
    Extrair JSON de resposta LLM.
    
    Tenta em ordem:
    1. Regex para {...}
    2. Parse direto do conteúdo
    
    Args:
        content: Conteúdo da resposta LLM
        
    Returns:
        Dict parseado ou None se falhar
    """
    # Tentativa 1: Procurar por JSON no formato {...}
    json_match = re.search(r'\{.*\}', content, re.DOTALL)
    if json_match:
        try:
            json_str = json_match.group(0)
            return json.loads(json_str)
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug(f"Erro ao parsear JSON extraído: {e}")
    
    # Tentativa 2: Parse direto do conteúdo
    try:
        return json.loads(content)
    except (json.JSONDecodeError, ValueError) as e:
        logger.debug(f"Erro ao parsear conteúdo como JSON: {e}")
        return None


class MessageResponse:
    """Resposta compatível com LangChain"""
    def __init__(self, content: str):
        self.content = content


class AzureFoundryLocalLLM:
    """Wrapper para Azure AI Foundry Local com compatibilidade LangChain"""
    
    def __init__(self, model: str, endpoint: str = None, max_tokens: int = 512, temperature: float = 0.7, structured_temperature: float = 0.3, timeout: int = 120):
        """
        Inicializar cliente Azure Foundry Local
        
        Args:
            model: ID do modelo (ex: "Phi-4-mini-instruct-generic-gpu:5")
            endpoint: URL do servidor Foundry (default: FOUNDRY_ENDPOINT)
            timeout: Timeout em segundos (default: 120)
        """
        self.model = model
        self.max_tokens = max_tokens
        self.temperature = temperature
        self.structured_temperature = structured_temperature
        self.timeout = timeout
        if endpoint is None:
            endpoint = FOUNDRY_ENDPOINT
        self.endpoint = endpoint.rstrip('/')
        self.api_url = f"{self.endpoint}/v1/chat/completions"
        self.api_key = FOUNDRY_API_KEY
        logger.info(f"✅ Conectado ao Foundry em {endpoint}")
    
    def invoke(self, prompt: str) -> MessageResponse:
        """
        Executar prompt simples
        
        Args:
            prompt: Texto do prompt
            
        Returns:
            MessageResponse com o conteúdo da resposta
        """
        try:
            logger.debug(f"Invoking model: {self.model}")
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": self.temperature,
                "max_tokens": self.max_tokens
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "api-key": self.api_key,
            }

            data = _make_request(self.api_url, payload, headers, self.timeout)
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"Response length: {len(content)} chars")
            return MessageResponse(content)
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error ao invocar modelo {self.model}: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao invocar modelo {self.model}: {e}")
            raise
    
    def invoke_structured(self, prompt: str, schema: Type[T]) -> T:
        """
        Executar prompt com structured output (JSON)
        
        Args:
            prompt: Texto do prompt
            schema: Pydantic model para parsing da resposta
            
        Returns:
            Instância do schema com dados parseados
            
        Raises:
            ValueError: Se não conseguir parsear o JSON
        """
        try:
            logger.debug(f"Invoking structured model: {self.model}")
            
            # Adicionar instrução explícita para JSON
            structured_prompt = f"""{prompt}

CRITICAL: Respond ONLY with a valid JSON object. No other text before or after."""
            
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": structured_prompt}],
                "temperature": self.structured_temperature,
                "max_tokens": self.max_tokens
            }
            
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "api-key": self.api_key,
            }

            data = _make_request(self.api_url, payload, headers, self.timeout)
            content = data["choices"][0]["message"]["content"]
            logger.debug(f"Raw response: {content[:100]}...")
            
            # Tentar extrair e parsear JSON
            parsed_json = _extract_json(content)
            
            if parsed_json:
                try:
                    result = schema(**parsed_json)
                    logger.debug(f"✅ Structured output parseado com sucesso")
                    return result
                except Exception as e:
                    logger.warning(f"Erro ao validar JSON contra schema: {e}")
            
            # Se falhar, lançar erro
            logger.error(f"Não foi possível parsear resposta como JSON: {content[:200]}")
            raise ValueError(f"Não foi possível parsear resposta como JSON")
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP Error ao invocar modelo estruturado: {e}")
            raise
        except Exception as e:
            logger.error(f"Erro ao invocar modelo estruturado: {e}")
            raise
    
    def with_structured_output(self, schema: Type[T]):
        """
        Retornar runnable com structured output (compatível LangChain)
        
        Args:
            schema: Pydantic model para o output
            
        Returns:
            StructuredRunnable
        """
        logger.debug(f"Creating structured runnable for schema: {schema.__name__}")
        return StructuredRunnable(self, schema)


class StructuredRunnable:
    """Runnable para structured output compatível com LangChain"""
    
    def __init__(self, llm: AzureFoundryLocalLLM, schema: Type[T]):
        """
        Inicializar runnable estruturado
        
        Args:
            llm: Instância do AzureFoundryLocalLLM
            schema: Pydantic model para parsing
        """
        self.llm = llm
        self.schema = schema
    
    def invoke(self, prompt: str) -> T:
        """
        Invocar com structured output
        
        Args:
            prompt: Texto do prompt
            
        Returns:
            Instância do schema
        """
        return self.llm.invoke_structured(prompt, self.schema)
