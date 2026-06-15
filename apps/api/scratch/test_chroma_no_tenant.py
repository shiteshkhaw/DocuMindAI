import os
import chromadb
from dotenv import load_dotenv

load_dotenv(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api\.env")

api_key = os.getenv("CHROMA_API_KEY")

print("Initializing CloudClient with only database='default_database'...")
try:
    client = chromadb.CloudClient(
        api_key=api_key,
        database="default_database"
    )
    print("CloudClient initialized successfully!")
    print("Collections:", client.list_collections())
except Exception as e:
    print("Initialization failed:", e)
