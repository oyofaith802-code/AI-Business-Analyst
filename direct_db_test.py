import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host="127.0.0.1",
    port=5432,
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

try:
    cur = conn.cursor()

    print("Connected directly to PostgreSQL")
    print()

    cur.execute(
        """
        SELECT id, user_email, table_name
        FROM schema_memory
        WHERE table_name = %s
        """,
        ("test_sales",)
    )

    print("BEFORE:")
    for row in cur.fetchall():
        print(row)

    cur.execute(
        """
        UPDATE schema_memory
        SET user_email = %s
        WHERE table_name = %s
        """,
        ("solomonenamudu@gmail.com", "test_sales")
    )

    print()
    print("ROWS UPDATED:", cur.rowcount)

    conn.commit()

    cur.execute(
        """
        SELECT id, user_email, table_name
        FROM schema_memory
        WHERE table_name = %s
        """,
        ("test_sales",)
    )

    print()
    print("AFTER:")

    for row in cur.fetchall():
        print(row)

finally:
    cur.close()
    conn.close()