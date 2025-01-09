import asyncio
import asyncpg

async def check_table_structure():
    conn = await asyncpg.connect(
        user='admin',
        password='admin',
        database='mnfst_labs_dev',
        host='157.245.0.147',
        port=5432
    )
    
    try:
        # Get table structure
        result = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'avatar_analysis'
            ORDER BY ordinal_position;
        """)
        
        print("Avatar Analysis Table Structure:")
        for row in result:
            print(f"Column: {row['column_name']}")
            print(f"Type: {row['data_type']}")
            print(f"Nullable: {row['is_nullable']}")
            print("---")
            
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(check_table_structure()) 