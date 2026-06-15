import json
import logging
import asyncio
import httpx
from typing import AsyncGenerator, List
from llm.base import BaseLLMProvider, LLMMessage, StreamingChunk
from config import settings

logger = logging.getLogger("documind.llm.gemini")

class GeminiProvider(BaseLLMProvider):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or settings.GEMINI_API_KEY

    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout: float = 30.0,
    ) -> AsyncGenerator[StreamingChunk, None]:
        if not self.api_key:
            raise ValueError("Gemini API key is missing. Please set GEMINI_API_KEY in environment variables.")

        # Gemini supports model names like 'gemini-1.5-pro'
        # Base URL for streaming content
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:streamGenerateContent?key={self.api_key}"

        # Adapt messages to Gemini format: user -> user, assistant -> model
        contents = []
        system_instruction = None

        for msg in messages:
            if msg.role == "system":
                system_instruction = {
                    "parts": [{"text": msg.content}]
                }
            else:
                contents.append({
                    "role": "model" if msg.role == "assistant" else "user",
                    "parts": [{"text": msg.content}]
                })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens
            }
        }

        if system_instruction:
            payload["systemInstruction"] = system_instruction

        headers = {
            "Content-Type": "application/json"
        }

        retries = 3
        backoff = 1.0

        for attempt in range(1, retries + 1):
            try:
                async with httpx.AsyncClient(timeout=timeout) as client:
                    async with client.stream("POST", url, headers=headers, json=payload) as response:
                        if response.status_code != 200:
                            error_body = await response.aread()
                            raise httpx.HTTPStatusError(
                                f"Gemini error response: {response.status_code} - {error_body.decode('utf-8')}",
                                request=response.request,
                                response=response
                            )

                        # Gemini streamGenerateContent returns a JSON stream containing objects with candidate content
                        buffer = ""
                        async for chunk_bytes in response.aiter_bytes():
                            buffer += chunk_bytes.decode("utf-8")
                            
                            # Parse JSON objects out of the stream. Gemini sends chunks in a JSON array format or as text stream
                            # Let's clean and extract chunks safely
                            while True:
                                # Look for boundary comma or bracket since it's a JSON array
                                buffer = buffer.strip()
                                if not buffer:
                                    break
                                
                                # Gemini stream returns a JSON array: [ { ... }, { ... } ]
                                # We can parse json blocks by locating matching braces
                                if buffer.startswith("["):
                                    buffer = buffer[1:].strip()
                                if buffer.startswith(","):
                                    buffer = buffer[1:].strip()
                                
                                if not buffer.startswith("{"):
                                    break
                                
                                # Find closing brace
                                open_braces = 0
                                match_idx = -1
                                for idx, char in enumerate(buffer):
                                    if char == "{":
                                        open_braces += 1
                                    elif char == "}":
                                        open_braces -= 1
                                        if open_braces == 0:
                                            match_idx = idx
                                            break
                                
                                if match_idx == -1:
                                    # Incomplete JSON block, wait for more data
                                    break
                                
                                json_str = buffer[:match_idx + 1]
                                buffer = buffer[match_idx + 1:].strip()
                                
                                try:
                                    data = json.loads(json_str)
                                    candidates = data.get("candidates", [])
                                    usage = data.get("usageMetadata", {})
                                    
                                    chunk = StreamingChunk()
                                    if candidates:
                                        content = candidates[0].get("content", {})
                                        parts = content.get("parts", [])
                                        if parts:
                                            chunk.token = parts[0].get("text", "")
                                    
                                    if usage:
                                        chunk.prompt_tokens = usage.get("promptTokenCount")
                                        chunk.completion_tokens = usage.get("candidatesTokenCount")
                                        
                                    if chunk.token or chunk.prompt_tokens is not None:
                                        yield chunk
                                except Exception as e:
                                    logger.warning(f"Failed to parse Gemini chunk: {e}")
                        return

            except (httpx.HTTPError, asyncio.TimeoutError) as e:
                logger.error(f"Gemini API call failed on attempt {attempt}: {e}")
                if attempt == retries:
                    raise e
                await asyncio.sleep(backoff)
                backoff *= 2.0
