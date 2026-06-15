import time
import logging
import traceback
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.document import DocumentRepository
from schemas.document import IngestionStatus
from parsers.resolver import DocumentParserResolver
from cleaners.pipeline import ContentCleanerPipeline
from chunking.engine import SemanticBoundaryChunker
from embeddings.base import BaseEmbeddingProvider
from vectorstore.base import BaseVectorStore

logger = logging.getLogger(__name__)


class IngestionOrchestrator:
    def __init__(
        self,
        db: AsyncSession,
        embedding_provider: BaseEmbeddingProvider,
        vector_store: BaseVectorStore,
    ):
        self.db = db
        self.doc_repo = DocumentRepository(db)
        self.parser_resolver = DocumentParserResolver()
        self.cleaner_pipeline = ContentCleanerPipeline()
        self.chunker = SemanticBoundaryChunker(chunk_size=500, chunk_overlap=50)
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.collection_name = "documind_chunks"

    async def ingest_document(
        self,
        document_id: str,
        file_content: bytes,
        filename: str,
        mime_type: str | None = None,
        user_id: str | None = None,
        workspace_id: str | None = None,
    ) -> None:
        """
        Production ingestion pipeline:
        1. DB status → PROCESSING
        2. Parse document
        3. Clean text
        4. Semantic chunk
        5. Purge stale vectors (idempotent re-ingest)
        6. Generate embeddings (concurrent batching)
        7. Upsert to vector store
        8. Verify persistence
        9. DB status → PROCESSED
        """
        start_time = time.perf_counter()
        logger.info(f"[Ingestion] Starting for doc={document_id} file={filename}")

        doc_model = await self.doc_repo.get(document_id)
        if not doc_model:
            logger.error(f"[Ingestion] Document {document_id} not found in DB")
            return

        doc_model.status = "UPLOADING"
        doc_model.started_at = datetime.now(timezone.utc).replace(tzinfo=None)
        doc_model.progress_percentage = 5
        await self.db.commit()

        try:
            # ── 1. Parse ────────────────────────────────────────────────────
            doc_model.status = "PARSING"
            doc_model.progress_percentage = 15
            await self.db.commit()
            t0 = time.perf_counter()
            parsed_doc = await self.parser_resolver.parse_document(
                file_content, filename, mime_type
            )
            logger.info(
                f"[Ingestion] Parse: {(time.perf_counter()-t0)*1000:.1f}ms | "
                f"pages={parsed_doc.metadata.get('page_count', len(parsed_doc.pages))}"
            )

            if not parsed_doc.pages or all(not p.text.strip() for p in parsed_doc.pages):
                raise ValueError(
                    "The document does not contain any readable text content. "
                    "Scanned/image-only PDFs are not supported without OCR."
                )

            # ── 2. Clean ────────────────────────────────────────────────────
            doc_model.status = "CLEANING"
            doc_model.progress_percentage = 30
            await self.db.commit()
            t0 = time.perf_counter()
            for page in parsed_doc.pages:
                page.text = self.cleaner_pipeline.clean(page.text)
            logger.info(f"[Ingestion] Clean: {(time.perf_counter()-t0)*1000:.1f}ms")

            # ── 3. Chunk ────────────────────────────────────────────────────
            doc_model.status = "CHUNKING"
            doc_model.progress_percentage = 45
            await self.db.commit()
            t0 = time.perf_counter()
            chunks = self.chunker.split(document_id, parsed_doc.pages)
            logger.info(
                f"[Ingestion] Chunk: {(time.perf_counter()-t0)*1000:.1f}ms | "
                f"chunks={len(chunks)} | "
                f"avg_tokens={sum(c.token_count for c in chunks)//max(len(chunks),1)}"
            )

            if not chunks:
                raise ValueError("No text chunks could be generated from the cleaned content.")

            # ── 4. Purge stale vectors (idempotent) ─────────────────────────
            t0 = time.perf_counter()
            try:
                count_before = await self.vector_store.count(self.collection_name)
                await self.vector_store.delete(
                    collection_name=self.collection_name,
                    filter_meta={"document_id": document_id},
                )
                count_after = await self.vector_store.count(self.collection_name)
                logger.info(
                    f"[Ingestion] Vector purge: {(time.perf_counter()-t0)*1000:.1f}ms | "
                    f"doc={document_id} | count_before={count_before} | count_after={count_after} | "
                    f"purged={count_before - count_after} vectors"
                )
            except Exception as purge_err:
                # Non-fatal: log and continue (collection may not exist yet)
                logger.warning(f"[Ingestion] Vector purge skipped/failed (non-fatal): {purge_err}")

            # ── 5. Embed ────────────────────────────────────────────────────
            doc_model.status = "EMBEDDING"
            doc_model.progress_percentage = 60
            await self.db.commit()
            t0 = time.perf_counter()
            chunk_texts = [c.content for c in chunks]
            vectors = await self.embedding_provider.embed_documents(chunk_texts)
            logger.info(
                f"[Ingestion] Embed: {(time.perf_counter()-t0)*1000:.1f}ms | "
                f"vectors={len(vectors)} | dim={len(vectors[0]) if vectors else 0}"
            )

            # ── 6. Build metadata ───────────────────────────────────────────
            ids = [c.id for c in chunks]
            metadatas = []
            for c in chunks:
                meta = c.metadata.copy()
                meta["document_id"] = document_id
                meta["page_number"] = c.page_number
                meta["token_count"] = c.token_count
                meta["char_offset_start"] = c.char_offset_start
                meta["char_offset_end"] = c.char_offset_end
                meta["user_id"] = user_id or "unknown"
                meta["workspace_id"] = workspace_id or "unknown"
                metadatas.append(meta)

            # ── 7. Upsert ───────────────────────────────────────────────────
            doc_model.status = "INDEXING"
            doc_model.progress_percentage = 80
            await self.db.commit()
            t0 = time.perf_counter()
            await self.vector_store.create_collection(self.collection_name)
            await self.vector_store.upsert(
                collection_name=self.collection_name,
                ids=ids,
                vectors=vectors,
                documents=chunk_texts,
                metadatas=metadatas,
            )
            logger.info(f"[Ingestion] Upsert: {(time.perf_counter()-t0)*1000:.1f}ms")

            # ── 8. Verify ───────────────────────────────────────────────────
            t0 = time.perf_counter()
            try:
                collection_count = await self.vector_store.count(self.collection_name)
                logger.info(
                    f"[Ingestion] Verify: collection_count={collection_count}"
                )

                # Smoke-test: query using middle chunk's vector to avoid header/title bias
                test_idx = len(vectors) // 2
                test_query = await self.vector_store.query(
                    collection_name=self.collection_name,
                    query_vector=vectors[test_idx],
                    limit=1,
                    filter_meta={"document_id": document_id},
                )
                if not test_query:
                    raise RuntimeError(
                        f"Vector persistence verification failed: "
                        f"query for document_id={document_id} returned 0 results."
                    )
                logger.info(
                    f"[Ingestion] Verify OK: {(time.perf_counter()-t0)*1000:.1f}ms | "
                    f"best_score={test_query[0][1]:.4f}"
                )
            except Exception as ver_err:
                logger.error(f"[Ingestion] Verification FAILED: {ver_err}", exc_info=True)
                raise RuntimeError(
                    f"Vector DB persistence verification failed: {ver_err}"
                ) from ver_err

            # ── 9. Finalise ─────────────────────────────────────────────────
            total_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"[Ingestion] SUCCESS doc={document_id} total={total_ms:.1f}ms | "
                f"chunks={len(chunks)}"
            )

            merged_meta = dict(doc_model.metadata_json or {})
            merged_meta.update(parsed_doc.metadata)
            merged_meta["chunks_count"] = len(chunks)
            merged_meta["ingestion_duration_ms"] = round(total_ms, 1)

            doc_model.metadata_json = merged_meta
            doc_model.status = "COMPLETED"
            doc_model.progress_percentage = 100
            doc_model.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
            doc_model.error = None
            await self.db.commit()

        except Exception as e:
            error_trace = traceback.format_exc()
            logger.error(
                f"[Ingestion] FAILED doc={document_id}: {e}\n{error_trace}"
            )
            try:
                doc_model = await self.doc_repo.get(document_id)
                if doc_model:
                    doc_model.status = "FAILED"
                    doc_model.failure_reason = str(e)
                    doc_model.error = f"{type(e).__name__}: {str(e)}"
                    doc_model.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
                    await self.db.commit()
            except Exception as db_err:
                logger.error(
                    f"[Ingestion] Failed to write error state to DB: {db_err}"
                )
                await self.db.rollback()
            raise
