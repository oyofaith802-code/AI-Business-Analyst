from database import engine
from sqlalchemy import text


with engine.connect() as conn:

    conn.execute(
        text("""
        DROP TABLE IF EXISTS schema_memory;
        """)
    )


    conn.execute(
        text("""
        CREATE TABLE schema_memory (

            id SERIAL PRIMARY KEY,

            user_email TEXT NOT NULL,

            table_name TEXT NOT NULL,

            columns TEXT NOT NULL,

            UNIQUE(user_email, table_name)

        );
        """)
    )


    conn.commit()


print("schema_memory recreated successfully")