import asyncio
import httpx
import json

async def run_e2e_verification():
    base_url = "http://127.0.0.1:8000/api/v1"
    print("=" * 70)
    print("  DocuMind AI — End-To-End RAG Verification")
    print("=" * 70)

    # Step 1: Upload / Ingest a Document
    print("\n1. Ingesting test document...")
    doc_payload = {
        "name": "diagnostic_spec.txt",
        "content": (
            "DocuMind AI is a production-grade document intelligence platform. "
            "It features semantic RAG, dense vector search, and source-grounded answering. "
            "The architecture utilizes ChromaDB for document vector stores. "
            "The platform supports model engines like DeepSeek R1 and OpenAI GPT."
        )
    }
    
    upload_url = f"{base_url}/documents/upload"
    files = {
        "file": ("diagnostic_spec.txt", doc_payload["content"].encode("utf-8"), "text/plain")
    }
    
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            res = await client.post(upload_url, files=files)
            if res.status_code != 201:
                print(f"  ✗ Ingestion failed with status {res.status_code}: {res.text}")
                return
            doc_info = res.json()
            doc_id = doc_info["id"]
            print(f"  ✓ Document ingested successfully. ID: {doc_id}, Status: {doc_info['status']}")
    except Exception as e:
        print(f"  ✗ Ingestion call failed: {e}")
        return

    # Wait for background ingestion task to complete
    print("\n2. Waiting for document status to become READY...")
    ready = False
    for i in range(10):
        await asyncio.sleep(1.0)
        try:
            async with httpx.AsyncClient() as client:
                res = await client.get(f"{base_url}/documents")
                docs = res.json()
                doc = next((d for d in docs if d["id"] == doc_id), None)
                if doc:
                    print(f"     Poll {i+1}: Status is '{doc['status']}'")
                    if doc["status"] == "processed":
                        ready = True
                        break
                    elif doc["status"] == "failed":
                        print(f"  ✗ Ingestion worker reported failure: {doc.get('error')}")
                        return
        except Exception as e:
            print(f"     Poll {i+1} failed: {e}")
            
    if not ready:
        print("  ✗ Document ingestion timed out or failed to process.")
        return

    # Step 2: Create a Chat Session linked to the Document
    print("\n3. Creating Chat Session...")
    session_payload = {
        "title": "E2E Diagnostic Chat",
        "documentIds": [doc_id]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            res = await client.post(f"{base_url}/chat/sessions", json=session_payload)
            if res.status_code != 201:
                print(f"  ✗ Session creation failed: {res.text}")
                return
            session_info = res.json()
            session_id = session_info["id"]
            print(f"  ✓ Chat Session created. ID: {session_id}")
    except Exception as e:
        print(f"  ✗ Session creation call failed: {e}")
        return

    # Step 3: Send a RAG query
    print("\n4. Sending RAG Query (streaming chat)...")
    chat_payload = {
        "sessionId": session_id,
        "content": "Explain what DocuMind AI is and which vector database it uses.",
        "documentIds": [doc_id],
        "model": "documind-v3"
    }
    
    stream_url = f"{base_url}/chat/messages/stream"
    has_citations = False
    has_tokens = False
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", stream_url, json=chat_payload) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    print(f"  ✗ Streaming request failed with status {response.status_code}: {body.decode('utf-8')}")
                    return
                
                print(f"  ✓ Streaming response status 200. Reading events:")
                async for line in response.aiter_lines():
                    line = line.strip()
                    if not line or not line.startsWith("data: "):
                        continue
                    
                    data_str = line[6:]
                    if data_str == "[DONE]":
                        print("\n  ✓ Stream finished [DONE].")
                        break
                    
                    try:
                        event = json.loads(data_str)
                        if event["type"] == "citations":
                            citations = event["citations"]
                            print(f"\n  [Citations Received]: {len(citations)} source blocks")
                            for idx, c in enumerate(citations):
                                print(f"    - Source {idx+1}: {c['documentName']} (Page {c['pageNumber']}) | Snippet: '{c['snippet']}'")
                            if citations:
                                has_citations = True
                        elif event["type"] == "token":
                            token = event["content"]
                            print(token, end="", flush=True)
                            has_tokens = True
                        elif event["type"] == "error":
                            print(f"\n  ✗ Stream reported error: {event['content']}")
                    except Exception as parse_err:
                        # Print raw event if not standard JSON
                        print(f"\n  (Non-JSON chunk): {data_str}")
    except Exception as e:
        print(f"  ✗ Streaming call encountered error: {e}")
        return

    # Step 4: Verify Session Messages in database
    print("\n5. Verifying message history in database...")
    try:
        async with httpx.AsyncClient() as client:
            res = await client.get(f"{base_url}/chat/sessions/{session_id}")
            sess_details = res.json()
            messages = sess_details["messages"]
            print(f"  ✓ Session '{session_id}' has {len(messages)} total message(s) in history.")
            
            assistant_msg = next((m for m in messages if m["role"] == "assistant" and m["content"]), None)
            if assistant_msg:
                print(f"  ✓ Persisted Assistant Response: '{assistant_msg['content'][:120]}...'")
                print(f"  ✓ Citations count: {len(assistant_msg.get('citations') or [])}")
                if assistant_msg.get('citations'):
                    has_citations = True
            else:
                print("  ✗ Persisted assistant message not found or empty.")
    except Exception as e:
        print(f"  ✗ Verification failed: {e}")
        return

    print("\n" + "=" * 70)
    print("  VERIFICATION SUMMARY")
    print("=" * 70)
    if has_citations and has_tokens:
        print("  ✓ SUCCESS: Full RAG pipeline is fully operational!")
    else:
        print(f"  ✗ FAILURE: Citations={has_citations}, Tokens={has_tokens}")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    # Standard helper for line prefix checking
    str.startsWith = lambda self, prefix: self.startswith(prefix)
    asyncio.run(run_e2e_verification())
