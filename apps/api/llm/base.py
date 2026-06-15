from abc import ABC, abstractmethod
from typing import AsyncGenerator, List, Dict, Any
from pydantic import BaseModel

class LLMMessage(BaseModel):
    role: str
    content: str

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class StreamingChunk(BaseModel):
    token: str = ""
    prompt_tokens: int | None = None
    completion_tokens: int | None = None

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_stream(
        self,
        messages: List[LLMMessage],
        model: str,
        temperature: float = 0.2,
        max_tokens: int = 1000,
        timeout: float = 30.0,
    ) -> AsyncGenerator[StreamingChunk, None]:
        """
        Generate a token stream from the LLM provider.
        Yields StreamingChunk containing token or token usage.
        """
        if False:
            yield StreamingChunk()
