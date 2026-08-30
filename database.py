from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

import streamlit as st


# Load local .env variables
load_dotenv()


def get_config(key, default=None):
    """
    Get configuration from Streamlit Cloud Secrets first,
    then fall back to local environment variables.
    """

    try:
        value = st.secrets.get(key)

        if value is not None:
            return value

    except Exception:
        pass

    return os.getenv(key, default)


# Get database details
USER = get_config("DB_USER")
PASSWORD = get_config("DB_PASSWORD")
HOST = get_config("DB_HOST")
PORT = get_config("DB_PORT", "5432")
DATABASE = get_config("DB_NAME")


# Validate required settings
missing = []

if not USER:
    missing.append("DB_USER")

if not PASSWORD:
    missing.append("DB_PASSWORD")

if not HOST:
    missing.append("DB_HOST")

if not DATABASE:
    missing.append("DB_NAME")


if missing:
    raise RuntimeError(
        "Missing database configuration: "
        + ", ".join(missing)
    )


# Encode password safely for PostgreSQL URL
PASSWORD = quote_plus(str(PASSWORD))


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

            print(
                "Database connected successfully!"
            )

    except Exception as e:

        print(
            "Database connection failed:"
        )

        print(e)