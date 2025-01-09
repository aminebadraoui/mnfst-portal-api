import asyncio
from sqlalchemy import text
from app.core.database import AsyncSessionLocal

async def check_tables():
    async with AsyncSessionLocal() as session:
        # Check if tables exist
        result = await session.execute(text("""
            SELECT tablename 
            FROM pg_catalog.pg_tables 
            WHERE schemaname = 'public'
        """))
        tables = result.fetchall()
        print("Tables in database:")
        for table in tables:
            print(f"- {table[0]}")

        # Check projects table
        result = await session.execute(text("""
            SELECT * FROM projects LIMIT 1
        """))
        project = result.fetchone()
        print("\nSample project:", project)

        # Check users table
        result = await session.execute(text("""
            SELECT * FROM users LIMIT 1
        """))
        user = result.fetchone()
        print("\nSample user:", user)

if __name__ == "__main__":
    asyncio.run(check_tables()) 