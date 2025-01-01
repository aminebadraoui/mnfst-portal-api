from sqlalchemy import create_engine, inspect
from app.core.config import settings

def inspect_db():
    # Create engine
    engine = create_engine(settings.DATABASE_URL)
    
    # Create inspector
    inspector = inspect(engine)
    
    # Get all table names
    tables = inspector.get_table_names()
    print("\nExisting tables:")
    for table in tables:
        print(f"\n{table}:")
        # Get columns for each table
        columns = inspector.get_columns(table)
        for column in columns:
            print(f"  - {column['name']}: {column['type']} (nullable: {column['nullable']})")
        
        # Get foreign keys
        foreign_keys = inspector.get_foreign_keys(table)
        if foreign_keys:
            print("  Foreign Keys:")
            for fk in foreign_keys:
                print(f"    - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")

if __name__ == "__main__":
    inspect_db() 