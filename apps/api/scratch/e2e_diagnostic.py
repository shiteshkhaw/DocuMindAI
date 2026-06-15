"""
DocuMind AI — Full Pipeline E2E Diagnostic
Traces: ingestion → embedding → vector store → retrieval → orchestration
"""
import os
import sys
import asyncio
import logging

sys.path.append(os.path.abspath(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api"))
os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")

# Force .env loading before any imports
from dotenv import load_dotenv
load_dotenv(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api\.env")

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("e2e_diagnostic")

SEPARATOR = "=" * 70

async def run_diagnostic():
    print(f"\n{SEPARATOR}")
    print("  PHASE 0 — ENVIRONMENT CONFIGURATION AUDIT")
    print(SEPARATOR)

    required_vars = ["EMBEDDING_PROVIDER", "VECTOR_STORE_PROVIDER", "OPENAI_API_KEY", "GROQ_API_KEY"]
    for var in required_vars:
        val = os.getenv(var)
        if val:
            masked = val[:8] + "..." if len(val) > 8 else val
            print(f"  ✓ {var} = {masked}")
        else:
            print(f"  ✗ {var} = NOT SET")

    embedding_provider_name = os.getenv("EMBEDDING_PROVIDER", "not_set")
    print(f"\n  Active Embedding Provider: '{embedding_provider_name}'")

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  PHASE 1 — EMBEDDING PROVIDER INITIALIZATION")
    print(SEPARATOR)

    from embeddings.providers import MockEmbeddingProvider, OpenAIEmbeddingProvider, HuggingFaceInferenceProvider
    from config import settings

    provider_name = settings.EMBEDDING_PROVIDER.lower()
    print(f"  Configured Provider: '{provider_name}'")

    if provider_name == "mock":
        embed_provider = MockEmbeddingProvider()
        print("  ✓ MockEmbeddingProvider initialized (deterministic hashing, no API key required)")
        print("  ⚠ WARNING: Mock embeddings are NOT semantically meaningful — retrieval relevance will be near-zero")
    elif provider_name == "openai":
        key = settings.OPENAI_API_KEY
        if not key:
            print("  ✗ OPENAI_API_KEY missing — embedding will fail")
        else:
            embed_provider = OpenAIEmbeddingProvider(api_key=key)
            is_openrouter = key.startswith("sk-or-v1-")
            print(f"  ✓ OpenAIEmbeddingProvider initialized")
            print(f"    Key type: {'OpenRouter (proxied)' if is_openrouter else 'Native OpenAI'}")
            print(f"    Endpoint: {embed_provider.url}")
    elif provider_name == "huggingface":
        embed_provider = HuggingFaceInferenceProvider(api_key=settings.HF_API_KEY)
        print("  ✓ HuggingFaceInferenceProvider initialized")
    else:
        from embeddings.providers import MockEmbeddingProvider
        embed_provider = MockEmbeddingProvider()
        print(f"  ⚠ Unknown provider '{provider_name}' — falling back to Mock")

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  PHASE 2 — EMBEDDING GENERATION TEST")
    print(SEPARATOR)

    sample_text = "DocuMind AI is a production-grade document intelligence platform using semantic RAG."
    print(f"  Test input: '{sample_text[:60]}...'")
    
    try:
        embedding = await embed_provider.embed_query(sample_text)
        print(f"  ✓ Query embedding generated successfully")
        print(f"    Dimensions: {len(embedding)}")
        print(f"    Sample values (first 5): {[round(v, 5) for v in embedding[:5]]}")
        all_zero = all(v == 0.0 for v in embedding)
        print(f"    All-zero vector: {all_zero} {'← PROBLEM: Zero embeddings!' if all_zero else ''}")
    except Exception as e:
        print(f"  ✗ Embedding generation FAILED: {e}")
        return

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  PHASE 3 — CHROMADB INITIALIZATION & COLLECTION AUDIT")
    print(SEPARATOR)

    from vectorstore.chroma import ChromaVectorStore
    
    try:
        vector_store = ChromaVectorStore()
        print(f"  ✓ ChromaVectorStore initialized")
        
        # Check Chroma client type
        client_type = type(vector_store._client).__name__
        print(f"    Client type: {client_type}")
        
        # List all existing collections
        try:
            existing_collections = vector_store._client.list_collections()
            print(f"    Existing collections ({len(existing_collections)}):")
            for col in existing_collections:
                try:
                    col_obj = vector_store._client.get_collection(col.name)
                    count = col_obj.count()
                    print(f"      - '{col.name}': {count} vectors")
                except Exception as col_e:
                    print(f"      - '{col.name}': count error — {col_e}")
        except Exception as list_e:
            print(f"    ⚠ Could not list collections: {list_e}")
            
    except Exception as e:
        print(f"  ✗ ChromaVectorStore initialization FAILED: {e}")
        return

    INGESTION_COLLECTION = "documind_chunks"
    print(f"\n  Expected ingestion/retrieval collection: '{INGESTION_COLLECTION}'")
    
    try:
        col = vector_store._client.get_collection(INGESTION_COLLECTION)
        doc_count = col.count()
        print(f"  ✓ Collection '{INGESTION_COLLECTION}' exists with {doc_count} vectors")
        if doc_count == 0:
            print(f"  ✗ CRITICAL: Collection is EMPTY — no document ingestion has been stored here!")
            print(f"    Likely cause: EphemeralClient resets on each process restart")
    except Exception:
        print(f"  ✗ Collection '{INGESTION_COLLECTION}' does NOT EXIST — no document has been ingested!")
        print(f"    Likely cause: Either ingestion failed or using EphemeralClient which resets on restart")

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  PHASE 4 — INGESTION SIMULATION (Mini Document)")
    print(SEPARATOR)

    from parsers.resolver import DocumentParserResolver
    from cleaners.pipeline import ContentCleanerPipeline
    from chunking.engine import SemanticBoundaryChunker

    DIAG_DOC_ID = "doc-diagnostic-001"
    DIAG_COLLECTION = "documind_chunks"
    sample_doc_content = (
        "DocuMind AI is built on a production-grade retrieval-augmented generation (RAG) architecture. "
        "It parses PDF documents, segments content into semantic chunks, and generates dense vector embeddings. "
        "The platform uses ChromaDB as the vector store for high-performance cosine similarity retrieval. "
        "Users can upload documents and then ask precise questions grounded in the document context.\n\n"
        "The system supports multiple LLM providers including OpenAI, Groq, and Gemini. "
        "All retrieval results include page-level citation metadata for transparent sourcing."
    )

    print(f"  Ingesting diagnostic document (ID: {DIAG_DOC_ID})")

    resolver = DocumentParserResolver()
    cleaner = ContentCleanerPipeline()
    chunker = SemanticBoundaryChunker(chunk_size=80, chunk_overlap=10)

    parsed = await resolver.parse_document(sample_doc_content.encode("utf-8"), "diagnostic.txt", "text/plain")
    for p in parsed.pages:
        p.text = cleaner.clean(p.text)
    chunks = chunker.split(DIAG_DOC_ID, parsed.pages)
    print(f"  ✓ Parsed → Cleaned → {len(chunks)} chunks generated")

    chunk_texts = [c.content for c in chunks]
    try:
        vectors = await embed_provider.embed_documents(chunk_texts)
        print(f"  ✓ Generated {len(vectors)} embeddings, each dim={len(vectors[0])}")
    except Exception as e:
        print(f"  ✗ Embedding batch FAILED: {e}")
        return

    ids = [c.id for c in chunks]
    metadatas = []
    for c in chunks:
        meta = dict(c.metadata)
        meta["document_id"] = DIAG_DOC_ID
        meta["page_number"] = c.page_number
        meta["token_count"] = c.token_count
        meta["char_offset_start"] = c.char_offset_start
        meta["char_offset_end"] = c.char_offset_end
        metadatas.append(meta)

    try:
        await vector_store.create_collection(DIAG_COLLECTION)
        await vector_store.upsert(
            collection_name=DIAG_COLLECTION,
            ids=ids,
            vectors=vectors,
            documents=chunk_texts,
            metadatas=metadatas
        )
        post_count = vector_store._client.get_collection(DIAG_COLLECTION).count()
        print(f"  ✓ Upserted {len(chunks)} vectors → collection '{DIAG_COLLECTION}' now has {post_count} total vectors")
    except Exception as e:
        print(f"  ✗ Vector upsert FAILED: {e}")
        return

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  PHASE 5 — RETRIEVAL PIPELINE TEST")
    print(SEPARATOR)

    from retrieval.service import RetrievalService

    retrieval_service = RetrievalService(embed_provider, vector_store)
    test_queries = [
        "What is DocuMind AI?",
        "How does the RAG architecture work?",
        "What LLM providers are supported?",
    ]

    for query in test_queries:
        print(f"\n  Query: '{query}'")
        try:
            result = await retrieval_service.retrieve(
                query=query,
                document_ids=[DIAG_DOC_ID],
                limit=3,
                min_score=0.0  # No floor for diagnostics
            )
            print(f"  ✓ Retrieved {len(result.results)} chunks")
            for item in result.results:
                print(f"    Score: {item.score:.4f} | Page: {item.page_number} | Text: '{item.text[:80]}...'")
            
            if len(result.results) == 0:
                print(f"  ✗ Zero results — embedding dimensionality or metadata mismatch suspected")
        except Exception as e:
            print(f"  ✗ Retrieval FAILED: {e}")

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  PHASE 6 — LLM PROVIDER CONNECTIVITY TEST")
    print(SEPARATOR)

    from llm.registry import llm_registry

    test_models = [
        ("deepseek-r1", "Groq / Llama 3.3"),
        ("documind-v3", "OpenAI / gpt-4o-mini"),
    ]

    for model_name, label in test_models:
        provider_name_resolved, actual_model = llm_registry.resolve_model_route(model_name)
        print(f"\n  Model Alias: '{model_name}' ({label})")
        print(f"    → Provider: {provider_name_resolved}, Model: {actual_model}")
        
        try:
            provider = llm_registry.get_provider(provider_name_resolved)
            from llm.base import LLMMessage
            test_messages = [LLMMessage(role="user", content="Say 'OK' in one word.")]
            
            response_tokens = []
            async for chunk in provider.generate_stream(
                messages=test_messages,
                model=actual_model,
                max_tokens=20
            ):
                if chunk.token:
                    response_tokens.append(chunk.token)
            
            full_response = "".join(response_tokens)
            print(f"    ✓ Response received: '{full_response[:100]}'")
        except Exception as e:
            print(f"    ✗ LLM call FAILED: {e}")

    # ──────────────────────────────────────────────────────────────────────
    print(f"\n{SEPARATOR}")
    print("  DIAGNOSTIC SUMMARY")
    print(SEPARATOR)
    print("  Run complete. Review ✗ markers above for failure points.")
    print(f"{SEPARATOR}\n")

if __name__ == "__main__":
    asyncio.run(run_diagnostic())
