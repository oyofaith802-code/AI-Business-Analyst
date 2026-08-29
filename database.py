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


# Function to run SQL queries
def run_query(query):
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()


# Test connection
if __name__ == "__main__":
    try:
        with engine.connect() as conn:
            print("Database connected successfully!")
    except Exception as e:
        print("Database connection failed:")
        print(e)