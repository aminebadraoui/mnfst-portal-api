import asyncio
import asyncpg

async def add_task_id_columns():
    conn = await asyncpg.connect(
        user='admin',
        password='admin',
        database='mnfst_labs_dev',
        host='157.245.0.147',
        port=5432
    )

    try:
        # Add task_id column to all analysis tables
        await conn.execute('''
            ALTER TABLE product_analysis 
            ADD COLUMN IF NOT EXISTS task_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid();
            
            ALTER TABLE pattern_analysis 
            ADD COLUMN IF NOT EXISTS task_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid();
            
            ALTER TABLE pain_analysis 
            ADD COLUMN IF NOT EXISTS task_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid();
            
            ALTER TABLE avatar_analysis 
            ADD COLUMN IF NOT EXISTS task_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid();
            
            ALTER TABLE question_analysis 
            ADD COLUMN IF NOT EXISTS task_id UUID UNIQUE NOT NULL DEFAULT gen_random_uuid();
        ''')
        print("Successfully added task_id columns to all analysis tables.")
    except Exception as e:
        print(f"Error adding task_id columns: {str(e)}")
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(add_task_id_columns()) 