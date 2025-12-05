import httpx
from typing import Optional
import logging
import asyncio

from app.core.config import settings

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Service for interacting with DeepSeek API with fallback and retry"""

    def __init__(self):
        # Primary provider (artemox)
        self.primary_api_key = settings.deepseek_api_key
        self.primary_base_url = settings.deepseek_base_url
        self.primary_model = settings.deepseek_model

        # Fallback provider (deepseek official)
        self.fallback_api_key = settings.deepseek_fallback_api_key
        self.fallback_base_url = settings.deepseek_fallback_base_url
        self.fallback_model = settings.deepseek_fallback_model

        self.timeout = settings.deepseek_timeout
        self.max_retries = settings.llm_max_retries

        # Response limits
        self.max_tokens = settings.deepseek_max_tokens
        self.temperature = settings.deepseek_temperature

    async def _try_provider(
        self, api_key: str, base_url: str, model: str, messages: list, provider_name: str
    ) -> str:
        """Try to get response from a specific provider"""
        if not api_key:
            raise ValueError(f'{provider_name} API key not configured')

        payload = {
            'model': model,
            'messages': messages,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
        }

        headers = {'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(
                f'{base_url}/chat/completions', json=payload, headers=headers
            )
            response.raise_for_status()

            data = response.json()

            # Extract response text
            if 'choices' in data and len(data['choices']) > 0:
                return data['choices'][0]['message']['content']
            else:
                logger.error(f'Unexpected API response format from {provider_name}: {data}')
                raise ValueError(f'Invalid response format from {provider_name} API')

    async def query(self, text: str, system_prompt: Optional[str] = None) -> str:
        """
        Send query to DeepSeek API with fallback and retry

        Strategy:
        1. Try primary provider (artemox) with retry
        2. If fails, fallback to secondary provider (deepseek) with retry

        Args:
            text: User query text
            system_prompt: Optional system prompt for context

        Returns:
            str: LLM response text

        Raises:
            Exception: If all providers fail
        """
        # Prepare messages
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        messages.append({'role': 'user', 'content': text})

        last_error = None

        # Try primary provider (artemox)
        for attempt in range(self.max_retries):
            try:
                logger.info(
                    f'Trying primary provider (artemox), attempt {attempt + 1}/{self.max_retries}'
                )
                result = await self._try_provider(
                    self.primary_api_key,
                    self.primary_base_url,
                    self.primary_model,
                    messages,
                    'artemox',
                )
                logger.info('✓ Primary provider (artemox) succeeded')
                return result

            except Exception as e:
                last_error = e
                logger.warning(f'Primary provider (artemox) attempt {attempt + 1} failed: {str(e)}')
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(0.5)  # Short delay between retries

        # Fallback to secondary provider (deepseek)
        if self.fallback_api_key:
            logger.info('Falling back to secondary provider (deepseek)')

            for attempt in range(self.max_retries):
                try:
                    logger.info(
                        f'Trying fallback provider (deepseek), attempt {attempt + 1}/{self.max_retries}'
                    )
                    result = await self._try_provider(
                        self.fallback_api_key,
                        self.fallback_base_url,
                        self.fallback_model,
                        messages,
                        'deepseek',
                    )
                    logger.info('✓ Fallback provider (deepseek) succeeded')
                    return result

                except Exception as e:
                    last_error = e
                    logger.warning(
                        f'Fallback provider (deepseek) attempt {attempt + 1} failed: {str(e)}'
                    )
                    if attempt < self.max_retries - 1:
                        await asyncio.sleep(0.5)

        # All providers failed
        logger.error(f'All LLM providers failed. Last error: {str(last_error)}')
        raise Exception(f'All LLM providers failed: {str(last_error)}')


# Singleton instance
deepseek_service = DeepSeekService()
