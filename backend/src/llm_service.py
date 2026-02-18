"""
LLM Service — REUSED UNCHANGED from Phase 1.
 
This file handles all GPT text generation calls.
Notice: we did NOT change a single line from Phase 1.
This is the payoff of good service design.
"""
from openai import OpenAI, APIError, RateLimitError
from src.config import settings
import logging
import time
 
logger = logging.getLogger(__name__)
 
class LLMService:
    """Wrapper around the OpenAI Chat API with retry logic."""
 
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
        self.max_tokens = settings.max_tokens
 
    def generate(self, prompt: str, system_message: str = None,
                 temperature: float = 0.7, max_retries: int = 3) -> str:
        """Send a prompt to GPT and return the response text."""
        messages = []
        if system_message:
            messages.append({"role": "system", "content": system_message})
        messages.append({"role": "user", "content": prompt})
 
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=self.max_tokens,
                )
                return response.choices[0].message.content
            except RateLimitError:
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited. Waiting {wait_time}s...")
                time.sleep(wait_time)
            except APIError as e:
                logger.error(f"OpenAI API error: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
 
llm_service = LLMService()
