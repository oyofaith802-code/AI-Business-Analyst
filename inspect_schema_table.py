from database import engine
from sqlalchemy import text

with engine.connect() as conn:

    print("=== TABLE DEFINITION ===")

    result = conn.execute(
        text("""
            SELECT
                column_name,
                data_type,
                column_default,
                is_nullable
            FROM information_schema.columns
            WHERE table_name = 'schema_memory'
            ORDER BY ordinal_position
        """)
    )

    for row in result.fetchall():
        print(row)

    print()
    print("=== TABLE RULES ===")

    result = conn.execute(
        text("""
            SELECT
                schemaname,
                tablename,
                rulename,
                definition
            FROM pg_rules
            WHERE tablename = 'schema_memory'
        """)
    )

    rows = result.fetchall()

    if not rows:
        print("NO RULES FOUND")
    else:
        for row in rows:
            print(row)

    print()
    print("=== TABLE OID ===")

    result = conn.execute(
        text("""
            SELECT
                oid,
                relname,
                relkind
            FROM pg_class
            WHERE relname = 'schema_memory'
        """)
    )

    for row in result.fetchall():
        print(row)