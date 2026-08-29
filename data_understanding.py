from sqlalchemy import text
from database import engine


def get_table_schema(table_name):

    query = """
    SELECT 
        column_name,
        data_type
    FROM information_schema.columns
    WHERE table_name = :table_name;
    """

    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            {
                "table_name": table_name
            }
        )

        return result.fetchall()



def analyze_table(table_name):

    columns = get_table_schema(table_name)


    analysis = f"""
Dataset: {table_name}

Columns:
"""


    for column, dtype in columns:

        analysis += f"- {column} ({dtype})\n"


    return analysis