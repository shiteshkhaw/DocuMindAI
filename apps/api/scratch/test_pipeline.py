import os
import sys
import asyncio

# Setup path so we can import apps/api modules
sys.path.append(os.path.abspath(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api"))

from parsers.resolver import DocumentParserResolver
from cleaners.pipeline import ContentCleanerPipeline
from chunking.engine import SemanticBoundaryChunker
from embeddings.providers import MockEmbeddingProvider
from vectorstore.chroma import ChromaVectorStore
from retrieval.service import RetrievalService

async def main():
    print("=== STARTING PIPELINE INTEGRATION TEST ===")
    
    # 1. Parse testing
    print("\n1. Testing Parser Resolver...")
    resolver = DocumentParserResolver()
    sample_text = (
        "DocuMind AI is a production-grade AI intelligence system. It handles parsing and storage.\n\n"
        "Page 1 of 2\n\n"
        "The second page introduces neural embeddings and ChromaDB. It has robust async capabilities."
    )
    parsed_doc = await resolver.parse_document(
        file_content=sample_text.encode("utf-8"),
        filename="test_guide.txt",
        mime_type="text/plain"
    )
    print(f"Parsed page count: {len(parsed_doc.pages)}")
    for i, p in enumerate(parsed_doc.pages):
        print(f"  Page {p.page_number} length: {len(p.text)}")

    # 2. Cleaner testing
    print("\n2. Testing Cleaner Pipeline...")
    cleaner = ContentCleanerPipeline()
    for p in parsed_doc.pages:
        p.text = cleaner.clean(p.text)
        print(f"  Cleaned Page {p.page_number} length: {len(p.text)}")
        print(f"  Cleaned Text Sample: {repr(p.text[:60])}")

    # 3. Chunker testing
    print("\n3. Testing Chunker Engine...")
    chunker = SemanticBoundaryChunker(chunk_size=40, chunk_overlap=5)
    chunks = chunker.split("doc-test-123", parsed_doc.pages)
    print(f"Generated {len(chunks)} chunks:")
    for c in chunks:
        print(f"  - Chunk {c.chunk_index} (Page {c.page_number}, {c.token_count} tokens): {repr(c.content)}")

    # 4. Embeddings & Vector store testing
    print("\n4. Testing Vector Storage & Embeddings...")
    embed_provider = MockEmbeddingProvider()
    vector_store = ChromaVectorStore()
    
    # Ensure collection exists
    collection_name = "test_run_collection"
    await vector_store.create_collection(collection_name)
    
    texts = [c.content for c in chunks]
    vectors = await embed_provider.embed_documents(texts)
    ids = [c.id for c in chunks]
    metadatas = [c.metadata for c in chunks]
    
    print("Upserting vectors into Chroma...")
    await vector_store.upsert(
        collection_name=collection_name,
        ids=ids,
        vectors=vectors,
        documents=texts,
        metadatas=metadatas
    )
    print("Upsert complete.")

    # 5. Retrieval testing
    print("\n5. Testing Retrieval Engine...")
    retrieval_service = RetrievalService(embed_provider, vector_store)
    # Use retrieval with collection override by injecting name or matching our service setup
    # Note: Our RetrievalService default is "documind_chunks". Let's run a query directly on the vector store.
    
    query = "What is DocuMind AI?"
    query_vector = await embed_provider.embed_query(query)
    results = await vector_store.query(
        collection_name=collection_name,
        query_vector=query_vector,
        limit=2
    )
    print(f"Query: '{query}'")
    print(f"Found {len(results)} matches:")
    for r_id, score, doc, meta in results:
        print(f"  Match ID: {r_id}, Similarity: {score:.4f}")
        print(f"  Content: {repr(doc)}")
        print(f"  Metadata: {meta}")

    # Cleanup
    print("\nCleaning up collection...")
    await vector_store.delete_collection(collection_name)
    print("=== PIPELINE INTEGRATION TEST PASSED SUCCESSFUL ===")

if __name__ == "__main__":
    asyncio.run(main())
