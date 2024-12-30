import asyncio
import asyncpg
from pprint import pprint

async def inspect_database():
    # Connect to the database with properly formatted connection string
    conn = await asyncpg.connect(
        host='143.198.172.101',
        port=5432,
        user='contact@mnfstai.com',
        password='invictus',
        database='mnfstportal_db'
    )
    
    # Get all tables
    tables = await conn.fetch("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    
    schema = {}
    
    # For each table, get its columns and constraints
    for table in tables:
        table_name = table['table_name']
        
        # Get columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = $1
            ORDER BY ordinal_position
        """, table_name)
        
        # Get primary key
        pk = await conn.fetch("""
            SELECT c.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.constraint_column_usage AS ccu USING (constraint_schema, constraint_name)
            JOIN information_schema.columns AS c ON c.table_schema = tc.constraint_schema
                AND tc.table_name = c.table_name AND ccu.column_name = c.column_name
            WHERE constraint_type = 'PRIMARY KEY' AND tc.table_name = $1
        """, table_name)
        
        # Get foreign keys
        fks = await conn.fetch("""
            SELECT
                kcu.column_name,
                ccu.table_name AS foreign_table_name,
                ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
                ON tc.constraint_name = kcu.constraint_name
                AND tc.table_schema = kcu.table_schema
            JOIN information_schema.constraint_column_usage AS ccu
                ON ccu.constraint_name = tc.constraint_name
                AND ccu.table_schema = tc.table_schema
            WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = $1
        """, table_name)
        
        schema[table_name] = {
            'columns': [dict(col) for col in columns],
            'primary_key': [pk_col['column_name'] for pk_col in pk],
            'foreign_keys': [dict(fk) for fk in fks]
        }
    
    await conn.close()
    return schema

if __name__ == "__main__":
    schema = asyncio.run(inspect_database())
    print("\nDatabase Schema:")
    print("===============")
    for table_name, table_info in schema.items():
        print(f"\nTable: {table_name}")
        print("Columns:")
        for col in table_info['columns']:
            print(f"  - {col['column_name']}: {col['data_type']} "
                  f"(nullable: {col['is_nullable']}, default: {col['column_default']})")
        if table_info['primary_key']:
            print("Primary Key:", table_info['primary_key'])
        if table_info['foreign_keys']:
            print("Foreign Keys:")
            for fk in table_info['foreign_keys']:
                print(f"  - {fk['column_name']} -> {fk['foreign_table_name']}.{fk['foreign_column_name']}") 