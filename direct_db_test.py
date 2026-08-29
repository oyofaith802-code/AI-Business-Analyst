import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def main():
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
            ORDER BY id
            """,
            ("test_sales",)
        )

        print("SCHEMA MEMORY:")
        for row in cur.fetchall():
            print(row)

        cur.close()

    finally:
        conn.close()


if __name__ == "__main__":
    main()