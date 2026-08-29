from database import engine
from sqlalchemy import text
import json


# =====================================================
# CREATE DATASET MEMORY TABLE
# =====================================================

def create_dataset_memory_table():

    query = """
    CREATE TABLE IF NOT EXISTS dataset_memory (

        id SERIAL PRIMARY KEY,

        user_email TEXT NOT NULL,

        dataset_name TEXT NOT NULL,

        profile JSONB NOT NULL,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    );
    """

    with engine.connect() as conn:

        conn.execute(
            text(query)
        )

        conn.commit()


# =====================================================
# SAVE DATASET PROFILE
# =====================================================

def save_dataset_memory(
    user_email,
    dataset_name,
    profile
):

    query = """
    INSERT INTO dataset_memory
    (
        user_email,
        dataset_name,
        profile
    )

    VALUES
    (
        :user_email,
        :dataset_name,
        :profile
    );
    """

    with engine.connect() as conn:

        conn.execute(
            text(query),
            {
                "user_email": user_email,
                "dataset_name": dataset_name,
                "profile": json.dumps(profile)
            }
        )

        conn.commit()


# =====================================================
# GET DATASET MEMORY
# =====================================================

def get_dataset_memory(
    user_email,
    dataset_name
):

    query = """
    SELECT profile

    FROM dataset_memory

    WHERE user_email = :user_email

    AND dataset_name = :dataset_name

    ORDER BY id DESC

    LIMIT 1;
    """

    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            {
                "user_email": user_email,
                "dataset_name": dataset_name
            }
        )

        row = result.fetchone()

        if row:

            return row[0]

        return None


# =====================================================
# GET PROFILE
# =====================================================

def get_profile(
    user_email,
    dataset_name
):

    return get_dataset_memory(
        user_email,
        dataset_name
    )