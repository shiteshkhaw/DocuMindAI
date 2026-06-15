import os
import asyncio
import logging
from typing import List, Dict, Any, Tuple, cast
import chromadb
from chromadb.api.types import Embeddings, Metadatas, Where
from vectorstore.base import BaseVectorStore
from config import settings

logger = logging.getLogger(__name__)


class ChromaVectorStore(BaseVectorStore):
    """
    ChromaDB vector store implementation.

    Backend priority:
        1. Chroma Cloud  (CHROMA_API_KEY set)
        2. Chroma HTTP   (CHROMA_SERVER_HOST set)
        3. Persistent    (CHROMA_PERSIST_DIRECTORY set)
        4. Ephemeral     (development / fallback)

    The active backend is logged at INFO level on startup.
    A heartbeat() method is provided for health checks.
    """

    def __init__(self):
        _settings = settings
        host = _settings.CHROMA_SERVER_HOST
        port = _settings.CHROMA_SERVER_PORT
        persist_dir = _settings.CHROMA_PERSIST_DIRECTORY
        api_key = _settings.CHROMA_API_KEY
        tenant = _settings.CHROMA_TENANT
        database = _settings.CHROMA_DATABASE or "default_database"

        import sys
        is_testing = "pytest" in sys.modules or os.getenv("TESTING") == "true"

        if api_key:
            logger.info(
                f"[ChromaDB] Backend: CLOUD | Tenant: {tenant or 'auto-resolve'} | Database: {database}"
            )
            kwargs: Dict[str, Any] = {"api_key": api_key, "database": database}
            if tenant:
                kwargs["tenant"] = tenant
            try:
                self._client = chromadb.CloudClient(**kwargs)
                self._backend = "cloud"
            except Exception as e:
                logger.error(f"[ChromaDB] Failed to initialise CloudClient: {e}", exc_info=True)
                raise

        elif host:
            logger.info(f"[ChromaDB] Backend: HTTP | Host: {host}:{port}")
            try:
                self._client = chromadb.HttpClient(host=host, port=int(port))
                self._backend = "http"
            except Exception as e:
                logger.error(f"[ChromaDB] Failed to initialise HttpClient: {e}", exc_info=True)
                raise

        elif persist_dir:
            logger.info(f"[ChromaDB] Backend: PERSISTENT | Path: {persist_dir}")
            try:
                self._client = chromadb.PersistentClient(path=persist_dir)
                self._backend = "persistent"
            except Exception as e:
                logger.error(f"[ChromaDB] Failed to initialise PersistentClient: {e}", exc_info=True)
                raise

        else:
            if not is_testing:
                # Production environments must have an explicit backend configured
                raise ValueError(
                    "[ChromaDB] No backend configuration found (CHROMA_API_KEY, CHROMA_SERVER_HOST, "
                    "or CHROMA_PERSIST_DIRECTORY must be set). Ephemeral mode fallback is disabled in production."
                )
            logger.warning(
                "[ChromaDB] Backend: EPHEMERAL (in-memory). "
                "Data will not persist across restarts. Running in development/testing mode."
            )
            self._client = chromadb.EphemeralClient()
            self._backend = "ephemeral"

    @property
    def backend(self) -> str:
        return self._backend

    async def heartbeat(self) -> Dict[str, Any]:
        """
        Pings the Chroma backend and returns connectivity status.
        Used by the /health endpoint and startup diagnostics.
        """
        try:
            collections = await asyncio.to_thread(self._client.list_collections)
            # Retrieve tenant and database properties from client or env fallback
            tenant = getattr(self._client, "_tenant", None) or settings.CHROMA_TENANT or "default_tenant"
            database = getattr(self._client, "_database", None) or settings.CHROMA_DATABASE or "default_database"
            return {
                "status": "connected",
                "backend": self._backend,
                "collection_count": len(collections),
                "tenant": tenant,
                "database": database,
            }
        except Exception as e:
            logger.warning(f"[ChromaDB] Heartbeat failed: {e}")
            return {
                "status": "disconnected",
                "backend": self._backend,
                "error": str(e),
            }

    async def create_collection(self, collection_name: str) -> None:
        logger.info(f"[ChromaDB] get_or_create_collection '{collection_name}'")
        await asyncio.to_thread(
            self._client.get_or_create_collection,
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    async def delete_collection(self, collection_name: str) -> None:
        logger.info(f"[ChromaDB] Deleting collection '{collection_name}'")
        try:
            await asyncio.to_thread(self._client.delete_collection, name=collection_name)
        except Exception as e:
            logger.warning(f"[ChromaDB] Failed to delete collection '{collection_name}': {e}")

    async def upsert(
        self,
        collection_name: str,
        ids: List[str],
        vectors: List[List[float]],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> None:
        logger.info(
            f"[ChromaDB] Upserting {len(ids)} vectors into '{collection_name}'"
        )
        start = asyncio.get_event_loop().time()

        try:
            collection = await asyncio.to_thread(
                self._client.get_or_create_collection,
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            # Sanitise metadata: Chroma only accepts str | int | float | bool values
            cleaned: List[Dict[str, Any]] = []
            for meta in metadatas:
                clean: Dict[str, Any] = {}
                for k, v in meta.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean[k] = v
                    elif v is None:
                        pass  # omit None values
                    else:
                        clean[k] = str(v)
                cleaned.append(clean)

            await asyncio.to_thread(
                collection.upsert,
                ids=ids,
                embeddings=cast(Embeddings, vectors),
                documents=documents,
                metadatas=cast(Metadatas, cleaned),
            )

            elapsed_ms = (asyncio.get_event_loop().time() - start) * 1000
            total = await asyncio.to_thread(collection.count)
            logger.info(
                f"[ChromaDB] Upsert complete in {elapsed_ms:.1f}ms. "
                f"Collection '{collection_name}' now has {total} vector(s)."
            )
        except Exception as e:
            logger.error(
                f"[ChromaDB] Upsert failed for collection '{collection_name}': {e}",
                exc_info=True,
            )
            raise

    async def delete(
        self,
        collection_name: str,
        ids: List[str] | None = None,
        filter_meta: Dict[str, Any] | None = None,
    ) -> None:
        try:
            collection = await asyncio.to_thread(
                self._client.get_or_create_collection,
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            if ids is not None:
                await asyncio.to_thread(collection.delete, ids=ids)
            elif filter_meta is not None:
                where_clause: Dict[str, Any] = {}
                for k, v in filter_meta.items():
                    if isinstance(v, list):
                        where_clause[k] = {"$in": v}
                    else:
                        where_clause[k] = v
                await asyncio.to_thread(collection.delete, where=where_clause)
        except Exception as e:
            logger.error(
                f"[ChromaDB] Delete failed for collection '{collection_name}': {e}",
                exc_info=True,
            )
            # Re-raise so callers can decide how to handle
            raise

    async def query(
        self,
        collection_name: str,
        query_vector: List[float],
        limit: int = 5,
        filter_meta: Dict[str, Any] | None = None,
    ) -> List[Tuple[str, float, str, Dict[str, Any]]]:
        logger.debug(
            f"[ChromaDB] Querying '{collection_name}' limit={limit} filters={filter_meta}"
        )
        start = asyncio.get_event_loop().time()

        try:
            collection = await asyncio.to_thread(
                self._client.get_or_create_collection,
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )

            where_clause: Where | None = None
            if filter_meta:
                built: Dict[str, Any] = {}
                for k, v in filter_meta.items():
                    if isinstance(v, list):
                        built[k] = {"$in": v}
                    else:
                        built[k] = v
                where_clause = cast(Where, built)

            results = await asyncio.to_thread(
                collection.query,
                query_embeddings=[query_vector],
                n_results=limit,
                where=where_clause,
            )

            formatted: List[Tuple[str, float, str, Dict[str, Any]]] = []
            ids_list = results.get("ids")
            if ids_list and len(ids_list) > 0 and len(ids_list[0]) > 0:
                for idx in range(len(ids_list[0])):
                    doc_id = ids_list[0][idx]
                    distances = results.get("distances")
                    distance = distances[0][idx] if distances and distances[0] else 0.5
                    # Cosine distance from Chroma: 0 = identical, 2 = opposite
                    # Convert to similarity: similarity = 1.0 - distance
                    score = max(0.0, min(1.0, 1.0 - distance))

                    docs = results.get("documents")
                    document = docs[0][idx] if docs and docs[0] else ""

                    metas = results.get("metadatas")
                    metadata: Dict[str, Any] = cast(Dict[str, Any], metas[0][idx]) if metas and metas[0] else {}

                    formatted.append((doc_id, score, document, metadata))

            elapsed_ms = (asyncio.get_event_loop().time() - start) * 1000
            logger.info(
                f"[ChromaDB] Query on '{collection_name}' returned {len(formatted)} result(s) "
                f"in {elapsed_ms:.1f}ms"
            )
            return formatted

        except Exception as e:
            # Distinguish between "collection empty" (safe to return []) and real errors
            err_str = str(e).lower()
            if "does not exist" in err_str or "not found" in err_str:
                logger.warning(
                    f"[ChromaDB] Collection '{collection_name}' not found during query. "
                    f"Returning empty results."
                )
                return []
            logger.error(
                f"[ChromaDB] Query error on '{collection_name}': {e}", exc_info=True
            )
            # Re-raise unexpected errors so callers get proper feedback
            raise

    async def count(self, collection_name: str) -> int:
        try:
            collection = await asyncio.to_thread(
                self._client.get_or_create_collection,
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            return await asyncio.to_thread(collection.count)
        except Exception as e:
            logger.error(f"[ChromaDB] Count error for '{collection_name}': {e}")
            return 0
