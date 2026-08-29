from database import engine
from sqlalchemy import text

with engine.connect() as conn:
    print("DATABASE:")
    print(conn.execute(text("SELECT current_database()")).scalar())

    print("\nUSER:")
    print(conn.execute(text("SELECT current_user")).scalar())

    print("\nHOST:")
    print(conn.execute(text("SELECT inet_server_addr()")).scalar())

    print("\nPORT:")
    print(conn.execute(text("SELECT inet_server_port()")).scalar())

    print("\nSCHEMA:")
    print(conn.execute(text("SELECT current_schema()")).scalar())

    print("\nEMAIL ROW:")
    result = conn.execute(
        text("""
            SELECT id, user_email, table_name
            FROM schema_memory
            WHERE table_name = :table
        """),
        {"table": "test_sales"}
    )

    for row in result.fetchall():
        print(row)