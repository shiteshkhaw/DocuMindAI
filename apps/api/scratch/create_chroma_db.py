import os
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

load_dotenv(r"c:\Users\khaws\Desktop\Interns\DocuMind AI\apps\api\.env")

api_key = os.getenv("CHROMA_API_KEY")
tenant = "bf7acfe8-2653-4cc7-b5ae-65207f4e92dc"

print("Initializing AdminClient...")
try:
    # On Chroma Cloud, AdminClient can be initialized via Settings
    settings = Settings(
        chroma_api_impl="chromadb.api.fastapi.FastAPI",
        chroma_server_host="api.trychroma.com",
        chroma_server_http_port=443,
        chroma_server_ssl_enabled=True,
        chroma_client_auth_provider="chromadb.auth.token_authn.TokenAuthClientProvider",
        chroma_client_auth_credentials=api_key,
        chroma_auth_token_transport_header="X-Chroma-Token"
    )
    admin_client = chromadb.AdminClient(settings=settings)
    print("AdminClient initialized successfully!")
    
    # Try to list databases
    print("Listing databases for tenant...")
    try:
        dbs = admin_client.list_databases(tenant=tenant)
        print("Databases:", dbs)
    except Exception as e:
        print("Failed to list databases:", e)

    # Try to create database 'documind'
    print("\nCreating database 'documind'...")
    try:
        admin_client.create_database(name="documind", tenant=tenant)
        print("Database 'documind' created successfully!")
    except Exception as e:
        print("Failed to create database 'documind':", e)
        
    # Try to create database 'default_database'
    print("\nCreating database 'default_database'...")
    try:
        admin_client.create_database(name="default_database", tenant=tenant)
        print("Database 'default_database' created successfully!")
    except Exception as e:
        print("Failed to create database 'default_database':", e)

except Exception as e:
    print("AdminClient setup failed:", e)
