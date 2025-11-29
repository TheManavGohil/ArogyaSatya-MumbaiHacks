"""
Shared LLM instance with caching for better performance.
"""
import hashlib
import json
from functools import lru_cache
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from app.core.config import settings

# Shared LLM instance - reused across all agents
_llm_instance: Optional[ChatGroq] = None

def get_llm() -> ChatGroq:
    """Get or create the shared LLM instance."""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",  # Fast model
            api_key=settings.GROQ_API_KEY,
            max_retries=2,
            request_timeout=30,
        )
    return _llm_instance


# Simple in-memory cache for LLM responses
_response_cache = {}
MAX_CACHE_SIZE = 100


def _get_cache_key(prompt: str) -> str:
    """Generate a cache key from prompt."""
    return hashlib.md5(prompt.encode()).hexdigest()


def cached_llm_invoke(prompt: str, use_cache: bool = True) -> str:
    """
    Invoke LLM with caching support.
    
    Args:
        prompt: The prompt to send to the LLM
        use_cache: Whether to use cached responses
        
    Returns:
        The LLM response content as string
    """
    cache_key = _get_cache_key(prompt)
    
    # Check cache first
    if use_cache and cache_key in _response_cache:
        print("[CACHE HIT] Using cached LLM response")
        return _response_cache[cache_key]
    
    # Make the actual call
    llm = get_llm()
    response = llm.invoke([SystemMessage(content=prompt)])
    result = response.content
    
    # Store in cache (with size limit)
    if len(_response_cache) >= MAX_CACHE_SIZE:
        # Remove oldest entry (simple FIFO)
        oldest_key = next(iter(_response_cache))
        del _response_cache[oldest_key]
    
    _response_cache[cache_key] = result
    return result


def clear_cache():
    """Clear the response cache."""
    global _response_cache
    _response_cache = {}

