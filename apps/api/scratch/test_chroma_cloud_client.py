import os
import chromadb
from dotenv import load_dotenv

load_dotenv(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api\.env")

api_key = os.getenv("CHROMA_API_KEY")
tenant = "bf7acfe8-2653-4cc7-b5ae-65207f4e92dc"

print("Trying initialization with tenant BF7... and database default_database")
try:
    client = chromadb.CloudClient(
        api_key=api_key,
        tenant=tenant,
        database="default_database"
    )
    print("CloudClient initialized successfully!")
    print("Collections:", client.list_collections())
except Exception as e:
    print("Initialization failed:", e)

print("\nTrying to create database 'default_database' if it doesn't exist?")
# Let's see if we can create or if we need to initialize with database=None to create?
# But database=None failed with "Could not determine a database name"
# Let's try initializing with different databases
for db_name in ["default_database", "default", "documind"]:
    print(f"\nTrying with database={db_name}")
    try:
        client = chromadb.CloudClient(
            api_key=api_key,
            tenant=tenant,
            database=db_name
        )
        print(f"Success with {db_name}!")
        print("Collections:", client.list_collections())
    except Exception as e:
        print(f"Failed with {db_name}: {e}")
