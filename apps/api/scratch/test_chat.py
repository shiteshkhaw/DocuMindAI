import asyncio
import httpx

async def test_chat_stream():
    # 1. First, check if the server is healthy
    url_root = "http://127.0.0.1:8000/"
    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            res = await client.get(url_root)
            print(f"Health Check: {res.status_code} - {res.json()}")
    except Exception as e:
        print(f"Failed health check: {e}")
        return

    # 2. Get active sessions
    url_sessions = "http://127.0.0.1:8000/api/v1/chat/sessions"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            res = await client.get(url_sessions)
            sessions = res.json()
            print(f"Found {len(sessions)} chat sessions.")
            if not sessions:
                print("No sessions found, cannot run message test. Create a session in the UI first.")
                return
            
            target_session_id = sessions[0]["id"]
            doc_ids = sessions[0]["documentIds"]
            print(f"Using Session ID: {target_session_id}")
            print(f"Focused Document IDs: {doc_ids}")
    except Exception as e:
        print(f"Failed to get sessions: {e}")
        return

    # 3. Post a streaming message to the session
    url_stream = "http://127.0.0.1:8000/api/v1/chat/messages/stream"
    payload = {
        "sessionId": target_session_id,
        "content": "Provide a concise summary of the active document.",
        "documentIds": doc_ids,
        "model": "deepseek-r1"
    }
    
    print("\nSending stream message request...")
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            async with client.stream("POST", url_stream, json=payload) as response:
                print(f"Response Status: {response.status_code}")
                if response.status_code != 200:
                    body = await response.aread()
                    print(f"Error Response Body: {body.decode('utf-8')}")
                    return
                
                async for line in response.aiter_lines():
                    print(f"Stream Chunk: {line}")
    except Exception as e:
        print(f"Streaming error: {e}")

if __name__ == "__main__":
    asyncio.run(test_chat_stream())
