import httpx
from typing import Optional
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Service for interacting with DeepSeek API"""
    
    def __init__(self):
        self.api_key = settings.deepseek_api_key
        self.base_url = settings.deepseek_base_url
        self.model = settings.deepseek_model
        self.timeout = settings.deepseek_timeout
        
    async def query(self, text: str, system_prompt: Optional[str] = None) -> str:
        """
        Send query to DeepSeek API and get response
        
        Args:
            text: User query text
            system_prompt: Optional system prompt for context
            
        Returns:
            str: LLM response text
            
        Raises:
            Exception: If API request fails
        """
        if not self.api_key:
            raise ValueError("DeepSeek API key not configured")
        
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": text})
        
        # Prepare request payload
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers
                )
                response.raise_for_status()
                
                data = response.json()
                
                # Extract response text
                if "choices" in data and len(data["choices"]) > 0:
                    return data["choices"][0]["message"]["content"]
                else:
                    logger.error(f"Unexpected API response format: {data}")
                    raise ValueError("Invalid response format from DeepSeek API")
                    
        except httpx.HTTPStatusError as e:
            logger.error(f"DeepSeek API HTTP error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"DeepSeek API error: {e.response.status_code}")
        except httpx.TimeoutException:
            logger.error("DeepSeek API request timeout")
            raise Exception("DeepSeek API timeout")
        except Exception as e:
            logger.error(f"DeepSeek API unexpected error: {str(e)}")
            raise


# Singleton instance
deepseek_service = DeepSeekService()

