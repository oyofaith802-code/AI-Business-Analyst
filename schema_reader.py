from sqlalchemy import create_engine, text


DATABASE_URL = "postgresql://postgres:2005Solomon%40@localhost:5432/business_ai"

engine = create_engine(DATABASE_URL)


def get_table_schema(table_name):

    query = text("""
        SELECT 
            column_name,
            data_type
        FROM information_schema.columns
        WHERE table_name = :table
        ORDER BY ordinal_position;
    """)


    with engine.connect() as conn:

        result = conn.execute(
            query,
            {
                "table": table_name
            }
        )


        schema = result.fetchall()


    return schema