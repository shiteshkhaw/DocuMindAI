from chunking.engine import SemanticBoundaryChunker


class MockParsedPage:
    def __init__(self, page_number: int, text: str) -> None:
        self.page_number = page_number
        self.text = text


def test_semantic_boundary_chunker_basic() -> None:
    chunker = SemanticBoundaryChunker(chunk_size=40, chunk_overlap=5)

    pages = [
        MockParsedPage(
            page_number=1,
            text="DocuMind AI is a production-grade intelligence system. It handles parsing and storage.",
        ),
        MockParsedPage(
            page_number=2,
            text="The second page introduces embeddings. It is extremely fast. We love testing software.",
        ),
    ]

    chunks = chunker.split("test-doc", pages)

    assert len(chunks) > 0
    assert chunks[0].document_id == "test-doc"
    assert chunks[0].chunk_index == 0
    assert chunks[0].metadata["document_id"] == "test-doc"
    assert "page_number" in chunks[0].metadata
    assert "token_count" in chunks[0].metadata


def test_semantic_boundary_chunker_empty() -> None:
    chunker = SemanticBoundaryChunker()
    assert chunker.split("empty-doc", []) == []


def test_semantic_boundary_chunker_large_sentence() -> None:
    """A sentence that exceeds chunk_size must still be included without looping."""
    chunker = SemanticBoundaryChunker(chunk_size=5, chunk_overlap=1)
    pages = [
        MockParsedPage(
            page_number=1,
            text="This is an extremely long sentence that contains many words and will exceed the limit.",
        )
    ]
    chunks = chunker.split("long-doc", pages)
    assert len(chunks) == 1
    assert "extremely long sentence" in chunks[0].content
