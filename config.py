"""Configuração centralizada do projeto Local Perplexity AI"""

import os
import logging
import sys
from dotenv import load_dotenv

load_dotenv()

# ============================================================================
# AZURE FOUNDRY SETTINGS
# ============================================================================
FOUNDRY_ENDPOINT = os.getenv("FOUNDRY_ENDPOINT", "http://127.0.0.1:52576")
FOUNDRY_API_KEY = os.getenv("FOUNDRY_API_KEY", "local")

# ============================================================================
# MODELOS LLM
# ============================================================================
# Modelo principal para gerar queries e resumir resultados
LLM_MODEL = "Phi-4-mini-instruct-generic-gpu:5"
LLM_MAX_TOKENS = 512
LLM_TEMPERATURE = 0.7
LLM_TIMEOUT = 120

# Modelo para raciocínio e gerar resposta final
REASONING_MODEL = "deepseek-r1-distill-qwen-7b-generic-gpu:3"
REASONING_MAX_TOKENS = 512
REASONING_TEMPERATURE = 0.3
REASONING_TIMEOUT = 300

# ============================================================================
# TAVILY SEARCH SETTINGS
# ============================================================================
TAVILY_MAX_RESULTS = 1
MAX_RAW_CHARS = 4000

# ============================================================================
# VERIFICATION SETTINGS
# ============================================================================
MAX_VERIFICATION_RETRIES = 2

# ============================================================================
# STREAMLIT SETTINGS
# ============================================================================
DEFAULT_QUERY = "How is the process of building a LLM?"
STREAMLIT_TITLE = "🌎 Local Perplexity"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logging(level: str = LOG_LEVEL) -> logging.Logger:
    """
    Configurar logging estruturado para o projeto.
    
    Args:
        level: Nível de logging (DEBUG, INFO, WARNING, ERROR)
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger("perplexity")
    
    # Não adicionar handlers duplicados
    if logger.handlers:
        return logger
    
    logger.setLevel(getattr(logging, level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    console_formatter = logging.Formatter(LOG_FORMAT)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler
    file_handler = logging.FileHandler("perplexity.log")
    file_handler.setLevel(getattr(logging, level))
    file_formatter = logging.Formatter(LOG_FORMAT)
    file_handler.setFormatter(console_formatter)
    logger.addHandler(file_handler)
    
    return logger


# ============================================================================
# VALIDAÇÃO DE CONFIGURAÇÃO
# ============================================================================
def validate_config() -> bool:
    """
    Validar se as configurações essenciais estão presentes.
    
    Returns:
        True se válido, False caso contrário
    """
    logger = setup_logging()
    
    # Validar endpoint do Foundry
    if not FOUNDRY_ENDPOINT:
        logger.error("❌ FOUNDRY_ENDPOINT não está configurado")
        return False
    
    logger.info(f"✅ Configuração carregada com sucesso")
    logger.debug(f"  - Endpoint: {FOUNDRY_ENDPOINT}")
    logger.debug(f"  - Modelo Principal: {LLM_MODEL}")
    logger.debug(f"  - Modelo Raciocínio: {REASONING_MODEL}")
    
    return True


# Inicializar logging ao importar o módulo
_logger = setup_logging()

__all__ = [
    "FOUNDRY_ENDPOINT",
    "FOUNDRY_API_KEY",
    "LLM_MODEL",
    "LLM_MAX_TOKENS",
    "LLM_TEMPERATURE",
    "LLM_TIMEOUT",
    "REASONING_MODEL",
    "REASONING_MAX_TOKENS",
    "REASONING_TEMPERATURE",
    "REASONING_TIMEOUT",
    "TAVILY_MAX_RESULTS",
    "MAX_RAW_CHARS",
    "MAX_VERIFICATION_RETRIES",
    "DEFAULT_QUERY",
    "STREAMLIT_TITLE",
    "LOG_LEVEL",
    "setup_logging",
    "validate_config",
]
