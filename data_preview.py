from sqlalchemy import create_engine, text
import pandas as pd


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

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