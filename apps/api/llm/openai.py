import json
import logging
import asyncio
import httpx
from typing import AsyncGenerator, List
from llm.base import BaseLLMProvider, LLMMessage, StreamingChunk
from config import settings

logger = logging.getLogger("documind.llm.openai")

class OpenAIProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.base_url = "https://api.openai.com/v1/chat/completions"

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout: float = 30.0,
    ) -> AsyncGenerator[StreamingChunk, None]:
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Please set OPENAI_API_KEY in environment variables.")

        base_url = self.base_url
        if self.api_key.startswith("sk-or-v1-"):
            base_url = "https://openrouter.ai/api/v1/chat/completions"
            if "/" not in model:
                model = f"openai/{model}"

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
            "stream_options": {"include_usage": True}
        }

        retries = 3
        backoff = 1.0

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", base_url, headers=headers, json=payload) as response:
                        if response.status_code != 200:
                            error_body = await response.aread()
                            raise httpx.HTTPStatusError(
                                f"OpenAI error response: {response.status_code} - {error_body.decode('utf-8')}",
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
                                    logger.warning(f"Failed to parse OpenAI SSE chunk: {e}")
                        # If we successfully parsed the stream, return
                        return

            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                logger.error(f"OpenAI API call failed on attempt {attempt}: {e}")
                if attempt == retries:
                    raise e
                await asyncio.sleep(backoff)
                backoff *= 2.0
