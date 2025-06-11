"""Robust LLM Client for Agent Magdala."""
import asyncio
import aiohttp
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from homeassistant.core import HomeAssistant
from homeassistant.util import dt as dt_util

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class LLMClient:
    """Robust LLM client with retry logic, timeout handling, and error recovery."""
    
    def __init__(self, hass: HomeAssistant, api_key: str, base_url: str = "https://openrouter.ai/api/v1"):
        self.hass = hass
        self._api_key = api_key  # Private to prevent logging
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.max_retries = 3
        self.timeout = 30
        self.backoff_factor = 2
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(
                timeout=timeout,
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                    "User-Agent": f"HomeAssistant-AgentMagdala/{DOMAIN}"
                }
            )
        return self.session
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "anthropic/claude-3-haiku",
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Send chat completion request with retry logic.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Returns:
            Response dict with 'choices' containing the completion
            
        Raises:
            LLMError: If all retries fail
        """
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }
        
        last_error = None
        
        for attempt in range(self.max_retries):
            try:
                session = await self._get_session()
                
                _LOGGER.debug(f"LLM request attempt {attempt + 1}/{self.max_retries} to model {model}")
                
                async with session.post(f"{self.base_url}/chat/completions", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        _LOGGER.debug(f"LLM request successful after {attempt + 1} attempts")
                        return result
                    
                    elif response.status == 429:  # Rate limit
                        wait_time = self.backoff_factor ** attempt
                        _LOGGER.warning(f"Rate limited, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    elif response.status >= 500:  # Server error
                        wait_time = self.backoff_factor ** attempt
                        _LOGGER.warning(f"Server error {response.status}, waiting {wait_time}s before retry")
                        await asyncio.sleep(wait_time)
                        continue
                    
                    else:  # Client error
                        error_text = await response.text()
                        # Don't log full error text as it might contain sensitive info
                        raise LLMError(f"HTTP {response.status}: Client error")
                        
            except asyncio.TimeoutError:
                last_error = LLMError(f"Request timeout after {self.timeout}s")
                _LOGGER.warning(f"LLM request timeout on attempt {attempt + 1}")
                
            except aiohttp.ClientError as e:
                last_error = LLMError(f"Network error: {type(e).__name__}")
                _LOGGER.warning(f"LLM network error on attempt {attempt + 1}: {type(e).__name__}")
                
            except Exception as e:
                last_error = LLMError(f"Unexpected error: {type(e).__name__}")
                _LOGGER.error(f"LLM unexpected error on attempt {attempt + 1}: {type(e).__name__}")
                
            # Wait before retry (except on last attempt)
            if attempt < self.max_retries - 1:
                wait_time = self.backoff_factor ** attempt
                await asyncio.sleep(wait_time)
        
        # All retries failed
        _LOGGER.error(f"LLM request failed after {self.max_retries} attempts")
        raise last_error or LLMError("All retry attempts failed")
    
    async def simple_completion(self, prompt: str, **kwargs) -> str:
        """
        Simple text completion interface.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional parameters for chat_completion
            
        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]
        
        try:
            response = await self.chat_completion(messages, **kwargs)
            
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"].strip()
            else:
                raise LLMError("No choices in response")
                
        except Exception as e:
            _LOGGER.error(f"Simple completion failed: {type(e).__name__}")
            raise LLMError(f"Completion failed: {type(e).__name__}")


class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass
