import json
import logging
import asyncio
import os
import httpx
from typing import AsyncGenerator, List
from llm.base import BaseLLMProvider, LLMMessage, StreamingChunk
from config import settings

logger = logging.getLogger("documind.llm.groq")

class GroqProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GROQ_API_KEY
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout: float = 30.0,
    ) -> AsyncGenerator[StreamingChunk, None]:
        if not self.api_key:
            raise ValueError("Groq API key is missing. Please set GROQ_API_KEY in environment variables.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": model,
            "messages": [msg.to_dict() for msg in messages],
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
        }

        retries = 3
        backoff = 1.0

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", self.base_url, headers=headers, json=payload) as response:
                        if response.status_code != 200:
                            error_body = await response.aread()
                            raise httpx.HTTPStatusError(
                                f"Groq error response: {response.status_code} - {error_body.decode('utf-8')}",
                                request=response.request,
                                response=response
                            )

                        async for line in response.aiter_lines():
                            line = line.strip()
                            if not line:
                                continue
                            if line.startswith("data: "):
                                data_str = line[len("data: "):]
                                if data_str == "[DONE]":
                                    break
                                
                                try:
                                    data = json.loads(data_str)
                                    choices = data.get("choices", [])
                                    usage = data.get("usage")
                                    
                                    chunk = StreamingChunk()
                                    if choices:
                                        delta = choices[0].get("delta", {})
                                        chunk.token = delta.get("content", "")
                                    
                                    if usage:
                                        chunk.prompt_tokens = usage.get("prompt_tokens")
                                        chunk.completion_tokens = usage.get("completion_tokens")
                                    
                                    if chunk.token or chunk.prompt_tokens is not None:
                                        yield chunk
                                except Exception as e:
                                    logger.warning(f"Failed to parse Groq SSE chunk: {e}")
                        return

            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                logger.error(f"Groq API call failed on attempt {attempt}: {e}")
                if attempt == retries:
                    raise e
                await asyncio.sleep(backoff)
                backoff *= 2.0
