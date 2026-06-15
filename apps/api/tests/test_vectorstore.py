from vectorstore.chroma import ChromaVectorStore


async def test_chroma_vector_store_lifecycle() -> None:
    """Full create → upsert → query → filter → delete → drop lifecycle."""
    store = ChromaVectorStore()
    collection = "test_pytest_collection"

    # 1. Create collection
    await store.create_collection(collection)

    # 2. Upsert – also validates metadata sanitisation (list → str, None dropped)
    ids = ["id-1", "id-2"]
    vectors = [[0.1] * 384, [0.9] * 384]
    documents = [
        "This is the first document text content.",
        "Second completely unrelated text.",
    ]
    metadatas = [
        {"document_id": "doc-a", "page_number": 1, "custom_list": [1, 2, 3]},
        {"document_id": "doc-b", "page_number": 2, "nullable_field": None},
    ]

    await store.upsert(
        collection_name=collection,
        ids=ids,
        vectors=vectors,
        documents=documents,
        metadatas=metadatas,
    )

    # 3. Query – vector close to id-2 should rank first
    results = await store.query(
        collection_name=collection,
        query_vector=[0.85] * 384,
        limit=1,
    )

    assert len(results) == 1
    r_id, score, text, meta = results[0]
    assert r_id == "id-2"
    assert text == "Second completely unrelated text."
    assert meta["document_id"] == "doc-b"
    assert "nullable_field" not in meta
    assert 0.0 <= score <= 1.0

    # 4. Metadata filter
    results_filtered = await store.query(
        collection_name=collection,
        query_vector=[0.15] * 384,
        limit=5,
        filter_meta={"document_id": "doc-a"},
    )
    assert len(results_filtered) == 1
    assert results_filtered[0][0] == "id-1"

    # 5. Delete by id
    await store.delete(collection_name=collection, ids=["id-1"])
    results_after_delete = await store.query(
        collection_name=collection,
        query_vector=[0.15] * 384,
        limit=5,
        filter_meta={"document_id": "doc-a"},
    )
    assert len(results_after_delete) == 0

    # 6. Drop collection
    await store.delete_collection(collection)
