from database import engine
from sqlalchemy import text


EMAIL = "solomonenamudu@gmail.com"
TABLE = "test_sales"


with engine.connect() as conn:

    result = conn.execute(
        text("""
            UPDATE public.schema_memory

            SET user_email = :email

            WHERE table_name = :table
        """),
        {
            "email": EMAIL,
            "table": TABLE
        }
    )

    conn.commit()

    print(
        "Rows updated:",
        result.rowcount
    )

    result = conn.execute(
        text("""
            SELECT
                id,
                user_email,
                table_name
            FROM public.schema_memory
            WHERE table_name = :table
        """),
        {
            "table": TABLE
        }
    )

    rows = result.fetchall()

    print("\nCurrent database value:")

    for row in rows:

        print(row)