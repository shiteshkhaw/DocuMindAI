import asyncio
import logging
from sqlalchemy import inspect, text
from db.session import engine

logging.basicConfig(level=logging.INFO)

async def check():
    async with engine.begin() as conn:
        def inspect_db(connection):
            inspector = inspect(connection)
            tables = inspector.get_table_names()
            print("TABLES:", tables)
            for table in tables:
                cols = [col["name"] for col in inspector.get_columns(table)]
                print(f"TABLE '{table}' COLUMNS:", cols)
        await conn.run_sync(inspect_db)

if __name__ == "__main__":
    asyncio.run(check())
