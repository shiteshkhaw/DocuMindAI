import logging
import asyncio
import hashlib
from typing import List, TypeVar, Callable, Awaitable
import httpx
from embeddings.base import BaseEmbeddingProvider

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retry(
    func: Callable[[], Awaitable[T]],
    retries: int = 3,
    initial_delay: float = 1.0,
    label: str = "operation"
) -> T:
    """Async retry helper with exponential backoff."""
    delay = initial_delay
    for attempt in range(retries):
        try:
            return await func()
        except Exception as e:
            if attempt == retries - 1:
                logger.error(f"[{label}] Failed after {retries} attempts: {e}")
                raise
            logger.warning(f"[{label}] Attempt {attempt + 1} failed. Retrying in {delay:.1f}s. Error: {e}")
            await asyncio.sleep(delay)
            delay *= 2.0
    raise RuntimeError(f"[{label}] with_retry exhausted all {retries} attempts")


class MockEmbeddingProvider(BaseEmbeddingProvider):
    """
    Deterministic Mock Embedding Provider for dev/test environments.
    Generates reproducible 384-dimension vectors using string hashing.
    NOT suitable for production semantic search.
    """
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def _generate_vector(self, text: str) -> List[float]:
        hash_bytes = hashlib.sha256(text.encode("utf-8")).digest()
        vector = []
        for i in range(self.dimension):
            byte_idx = (i * 3) % len(hash_bytes)
            val = (hash_bytes[byte_idx] / 127.5) - 1.0
            vector.append(val)
        return self.normalize(vector)

    async def embed_query(self, text: str) -> List[float]:
        await asyncio.sleep(0.01)
        return self._generate_vector(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        await asyncio.sleep(0.02)
        return [self._generate_vector(t) for t in texts]


class OpenAIEmbeddingProvider(BaseEmbeddingProvider):
    """
    OpenAI Embeddings API provider.
    Supports both OpenAI direct (sk-...) and OpenRouter (sk-or-v1-...) keys.
    Uses concurrent batching with semaphore for rate-limit safety.
    """
    def __init__(
        self,
        api_key: str,
        model: str = "text-embedding-3-small",
        dimension: int = 1536,
        batch_size: int = 64,
        max_concurrent_batches: int = 5,
    ):
        self.api_key = api_key
        self.dimension = dimension
        self.batch_size = batch_size
        self._semaphore = asyncio.Semaphore(max_concurrent_batches)

        if api_key.startswith("sk-or-v1-"):
            self.url = "https://openrouter.ai/api/v1/embeddings"
            self.model = model if "/" in model else f"openai/{model}"
        else:
            self.url = "https://api.openai.com/v1/embeddings"
            self.model = model

    async def _send_batch(self, input_texts: List[str]) -> List[List[float]]:
        """Send a single batch to the embeddings API (with semaphore guard)."""
        async with self._semaphore:
            async def task() -> List[List[float]]:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                }
                data = {"model": self.model, "input": input_texts}
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(self.url, headers=headers, json=data)
                    response.raise_for_status()
                    res_data = response.json()
                    embeddings = [
                        item["embedding"]
                        for item in sorted(res_data["data"], key=lambda x: x["index"])
                    ]
                    return [self.normalize(e) for e in embeddings]

            return await with_retry(task, label=f"OpenAI embed batch[{len(input_texts)}]")

    async def embed_query(self, text: str) -> List[float]:
        results = await self._send_batch([text])
        return results[0]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        # Split into batches
        batches: List[List[str]] = []
        for i in range(0, len(texts), self.batch_size):
            batches.append(texts[i : i + self.batch_size])

        logger.info(
            f"[OpenAI Embed] Embedding {len(texts)} texts in {len(batches)} concurrent batch(es)"
        )

        # Run all batches concurrently (semaphore controls parallelism)
        batch_results = await asyncio.gather(
            *[self._send_batch(batch) for batch in batches]
        )

        # Flatten results preserving order
        all_embeddings: List[List[float]] = []
        for batch_result in batch_results:
            all_embeddings.extend(batch_result)
        return all_embeddings


class HuggingFaceInferenceProvider(BaseEmbeddingProvider):
    """
    HuggingFace Serverless Inference API embedding provider.
    Model: BAAI/bge-small-en-v1.5 (384-dim)
    Uses concurrent batching with semaphore for rate-limit safety.
    """
    def __init__(
        self,
        api_key: str | None = None,
        model: str = "BAAI/bge-small-en-v1.5",
        batch_size: int = 32,
        max_concurrent_batches: int = 3,
    ):
        self.api_key = api_key
        self.model = model
        self.url = f"https://api-inference.huggingface.co/pipeline/feature-extraction/{model}"
        self.batch_size = batch_size
        self._semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def _send_batch(self, texts: List[str]) -> List[List[float]]:
        async with self._semaphore:
            async def task() -> List[List[float]]:
                headers: dict = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(
                        self.url, headers=headers, json={"inputs": texts}
                    )
                    response.raise_for_status()
                    embeddings = response.json()
                    if len(texts) == 1 and isinstance(embeddings[0], float):
                        embeddings = [embeddings]
                    return [self.normalize(e) for e in embeddings]

            return await with_retry(task, label=f"HF embed batch[{len(texts)}]")

    async def embed_query(self, text: str) -> List[float]:
        results = await self._send_batch([text])
        return results[0]

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        batches = [texts[i : i + self.batch_size] for i in range(0, len(texts), self.batch_size)]
        logger.info(
            f"[HF Embed] Embedding {len(texts)} texts in {len(batches)} concurrent batch(es)"
        )

        batch_results = await asyncio.gather(
            *[self._send_batch(batch) for batch in batches]
        )

        all_embeddings: List[List[float]] = []
        for batch_result in batch_results:
            all_embeddings.extend(batch_result)
        return all_embeddings


class GeminiEmbeddingProvider(BaseEmbeddingProvider):
    """
    Google Gemini Embeddings API provider.
    Uses concurrent batching + retry for reliable ingestion.
    """
    def __init__(
        self,
        api_key: str,
        model: str = "models/text-embedding-004",
        batch_size: int = 10,
        max_concurrent_batches: int = 3,
    ):
        self.api_key = api_key
        self.model = model
        self.url = f"https://generativelanguage.googleapis.com/v1beta/{model}:embedContent?key={api_key}"
        self.batch_size = batch_size
        self._semaphore = asyncio.Semaphore(max_concurrent_batches)

    async def _embed_single(self, text: str) -> List[float]:
        async with self._semaphore:
            data = {"content": {"parts": [{"text": text}]}}

            async def task() -> List[float]:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(self.url, json=data)
                    response.raise_for_status()
                    return self.normalize(response.json()["embedding"]["values"])

            return await with_retry(task, label="Gemini embed single")

    async def embed_query(self, text: str) -> List[float]:
        return await self._embed_single(text)

    async def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if not texts:
            return []

        logger.info(f"[Gemini Embed] Embedding {len(texts)} texts concurrently")
        results = await asyncio.gather(
            *[self._embed_single(text) for text in texts],
            return_exceptions=True
        )

        embeddings: List[List[float]] = []
        for idx, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"[Gemini Embed] Failed on text index {idx}: {result}")
                raise result
            embeddings.append(result)  # type: ignore[arg-type]
        return embeddings
