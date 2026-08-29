from database import engine
from sqlalchemy import text

with engine.connect() as conn:

    result = conn.execute(
        text("""
            SELECT
                trigger_name,
                event_manipulation,
                action_statement
            FROM information_schema.triggers
            WHERE event_object_table = 'schema_memory'
        """)
    )

    rows = result.fetchall()

    if not rows:
        print("NO TRIGGERS FOUND ON schema_memory")
    else:
        print("TRIGGERS FOUND:")
        for row in rows:
            print(row)