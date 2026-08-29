from database import engine
from sqlalchemy import text

with engine.connect() as conn:

    print("=== TABLE IDENTITY ===")

    result = conn.execute(
        text("""
            SELECT
                current_database() AS database_name,
                current_schema() AS schema_name,
                current_user AS database_user,
                pg_get_userbyid(c.relowner) AS owner,
                c.oid,
                c.relname,
                c.relkind,
                c.relispartition
            FROM pg_class c
            JOIN pg_namespace n
                ON n.oid = c.relnamespace
            WHERE n.nspname = 'public'
              AND c.relname = 'schema_memory'
        """)
    )

    for row in result.fetchall():
        print(row)

    print()
    print("=== INHERITANCE / PARTITIONS ===")

    result = conn.execute(
        text("""
            SELECT
                child.relname AS child_table,
                parent.relname AS parent_table
            FROM pg_inherits i
            JOIN pg_class child
                ON child.oid = i.inhrelid
            JOIN pg_class parent
                ON parent.oid = i.inhparent
            WHERE child.relname = 'schema_memory'
               OR parent.relname = 'schema_memory'
        """)
    )

    rows = result.fetchall()

    if not rows:
        print("NO INHERITANCE OR PARTITIONS FOUND")
    else:
        for row in rows:
            print(row)

    print()
    print("=== CURRENT ROW ===")

    result = conn.execute(
        text("""
            SELECT
                id,
                user_email,
                table_name,
                columns
            FROM public.schema_memory
            WHERE table_name = :table
        """),
        {"table": "test_sales"}
    )

    for row in result.fetchall():
        print(row)

    print()
    print("=== TEST UPDATE WITH RETURNING ===")

    result = conn.execute(
        text("""
            UPDATE public.schema_memory
            SET user_email = :email
            WHERE id = :id
            RETURNING id, user_email, table_name
        """),
        {
            "email": "plain_test_email@gmail.com",
            "id": 233
        }
    )

    for row in result.fetchall():
        print("RETURNING:", row)

    conn.commit()

    print()
    print("=== VERIFY AFTER COMMIT ===")

    result = conn.execute(
        text("""
            SELECT
                id,
                user_email,
                table_name
            FROM public.schema_memory
            WHERE id = :id
        """),
        {"id": 233}
    )

    for row in result.fetchall():
        print("VERIFY:", row)