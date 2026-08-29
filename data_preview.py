from sqlalchemy import create_engine, text
import pandas as pd


DATABASE_URL = "postgresql://postgres:2005Solomon%40@localhost:5432/business_ai"

engine = create_engine(DATABASE_URL)


def get_table_preview(table_name, limit=5):

    query = text(f"""
        SELECT *
        FROM {table_name}
        LIMIT {limit};
    """)


    with engine.connect() as conn:
        result = conn.execute(query)

        rows = result.fetchall()

        columns = result.keys()


    df = pd.DataFrame(
        rows,
        columns=columns
    )


    return df