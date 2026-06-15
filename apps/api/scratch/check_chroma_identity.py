import os
import requests
from dotenv import load_dotenv

load_dotenv(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api\.env")

api_key = os.getenv("CHROMA_API_KEY")
print("API Key:", api_key)

# Check identity with Authorization
resp = requests.get("https://api.trychroma.com/api/v2/auth/identity", headers={"Authorization": f"Bearer {api_key}"})
print("Authorization Header Status:", resp.status_code)
print("Authorization Header JSON:", resp.json())

# Check identity with X-Chroma-Token
resp2 = requests.get("https://api.trychroma.com/api/v2/auth/identity", headers={"X-Chroma-Token": api_key})
print("X-Chroma-Token Header Status:", resp2.status_code)
print("X-Chroma-Token Header JSON:", resp2.json())


# Check if we can list databases/tenants or what
# Let's inspect the tenants/databases from trychroma
# Usually trychroma has /api/v2/tenants or /api/v2/databases or similar?
# Let's see what identity json returns first.
