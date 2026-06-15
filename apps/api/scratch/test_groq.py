import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load env variables
load_dotenv(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api\.env")

async def test_groq():
    api_key = os.getenv("GROQ_API_KEY")
    url = "https://api.groq.com/openai/v1/models"
    headers = {
        "Authorization": f"Bearer {api_key}",
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, headers=headers)
            print(f"Status Code: {response.status_code}")
            if response.status_code == 200:
                models = response.json().get("data", [])
                print("Active Models on Groq:")
                for m in models:
                    print(f"  - {m['id']}")
            else:
                print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_groq())
