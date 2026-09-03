"""
Singh Ji Voice AI v3.0 - Error Handler
5-Layer LLM Fallback + 4-Layer STT Fallback
Graceful degradation with retry logic
"""

import asyncio
import logging
from functools import wraps
from typing import Callable, Any, Optional
import time

logger = logging.getLogger("singhji_voice")

# Retry decorator with exponential backoff
def retry_with_fallback(max_retries: int = 3, backoff_factor: float = 2.0):
    def decorator(func: Callable):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"{func.__name__} attempt {attempt+1}/{max_retries} failed: {str(e)}. Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
            logger.error(f"{func.__name__} failed after {max_retries} attempts: {str(last_exception)}")
            raise last_exception
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    wait_time = backoff_factor ** attempt
                    logger.warning(f"{func.__name__} attempt {attempt+1}/{max_retries} failed: {str(e)}. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
            logger.error(f"{func.__name__} failed after {max_retries} attempts: {str(last_exception)}")
            raise last_exception
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

# 5-Layer LLM Fallback Chain
LLM_FALLBACK_CHAIN = [
    "groq",      # Layer 1: Fastest, cheapest
    "gemini",    # Layer 2: Google backup
    "local",     # Layer 3: Local model (if available)
    "hf_inf",    # Layer 4: HuggingFace Inference API
    "rule"       # Layer 5: Rule-based (always works)
]

# 4-Layer STT Fallback Chain
STT_FALLBACK_CHAIN = [
    "hf_bucket",  # Layer 1: HF zero-stt-hinglish bucket
    "whisper",    # Layer 2: OpenAI Whisper
    "google",     # Layer 3: Google Speech Recognition
    "vosk"        # Layer 4: Offline Vosk (last resort)
]

class FallbackManager:
    """Manages fallback chains for LLM and STT"""
    
    def __init__(self):
        self.llm_status = {name: True for name in LLM_FALLBACK_CHAIN}
        self.stt_status = {name: True for name in STT_FALLBACK_CHAIN}
        self.circuit_breaker = {}  # Track failures per service
    
    def mark_failed(self, service_type: str, service_name: str):
        """Mark a service as temporarily failed"""
        if service_type == "llm":
            self.llm_status[service_name] = False
        elif service_type == "stt":
            self.stt_status[service_name] = False
        self.circuit_breaker[service_name] = time.time()
        logger.warning(f"Service {service_name} marked as failed. Circuit breaker active.")
    
    def is_available(self, service_type: str, service_name: str) -> bool:
        """Check if service is available (circuit breaker recovery)"""
        if service_name in self.circuit_breaker:
            # Auto-recover after 5 minutes
            if time.time() - self.circuit_breaker[service_name] > 300:
                self.circuit_breaker.pop(service_name)
                if service_type == "llm":
                    self.llm_status[service_name] = True
                elif service_type == "stt":
                    self.stt_status[service_name] = True
                logger.info(f"Service {service_name} auto-recovered.")
                return True
            return False
        return True
    
    def get_llm_chain(self) -> list:
        """Get available LLM services in priority order"""
        return [s for s in LLM_FALLBACK_CHAIN if self.is_available("llm", s)]
    
    def get_stt_chain(self) -> list:
        """Get available STT services in priority order"""
        return [s for s in STT_FALLBACK_CHAIN if self.is_available("stt", s)]

# Global fallback manager
fallback_mgr = FallbackManager()

# Timeout wrapper
async def with_timeout(coro, timeout: float = 10.0, fallback_value: Any = None):
    """Execute coroutine with timeout"""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        logger.error(f"Operation timed out after {timeout}s")
        if fallback_value is not None:
            return fallback_value
        raise

# Safe API caller
@retry_with_fallback(max_retries=2, backoff_factor=1.5)
async def safe_api_call(func: Callable, *args, **kwargs) -> Any:
    """Safely call an API function with retry and timeout"""
    return await with_timeout(func(*args, **kwargs), timeout=10.0)
