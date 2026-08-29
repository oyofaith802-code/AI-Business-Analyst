from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

# Get database details
USER = os.getenv("DB_USER")
PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DATABASE = os.getenv("DB_NAME")

# Create database engine
engine = create_engine(
    f"postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)


def run_query(query, params=None):
    """
    Execute a SQL query.

    Returns rows for SELECT/RETURNING queries.
    Returns [] for statements that do not return rows.
    """

    with engine.begin() as conn:
        result = conn.execute(
            text(query),
            params or {}
        )

        if result.returns_rows:
            return result.fetchall()

        return []


if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("Database connected successfully!")
    except Exception as e:
        print("Database connection failed:")
        print(e)