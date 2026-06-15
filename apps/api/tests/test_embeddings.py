import math
import pytest

from embeddings.providers import MockEmbeddingProvider


def test_normalization() -> None:
    provider = MockEmbeddingProvider()

    v = [3.0, 4.0]  # magnitude = sqrt(9 + 16) = 5.0
    norm_v = provider.normalize(v)
    assert norm_v == [0.6, 0.8]

    mag = math.sqrt(sum(x ** 2 for x in norm_v))
    assert pytest.approx(mag) == 1.0

    norm_zero = provider.normalize([0.0, 0.0])
    assert norm_zero == [0.0, 0.0]


async def test_mock_embedding_provider() -> None:
    provider = MockEmbeddingProvider(dimension=128)
    assert provider.dimension == 128

    text = "Hello DocuMind"
    vector = await provider.embed_query(text)

    assert len(vector) == 128
    mag = math.sqrt(sum(x**2 for x in vector))
    assert pytest.approx(mag) == 1.0

    # Deterministic: same text → same vector
    assert vector == await provider.embed_query(text)

    # Different text → different vector
    assert vector != await provider.embed_query("Different text")


async def test_mock_embedding_documents() -> None:
    provider = MockEmbeddingProvider(dimension=64)
    vectors = await provider.embed_documents(["Chunk 1 text content", "Chunk 2 text content"])

    assert len(vectors) == 2
    assert len(vectors[0]) == 64
    assert len(vectors[1]) == 64
