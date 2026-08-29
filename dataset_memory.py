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

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        UNIQUE(user_email, dataset_name)

    );
    """

    with engine.begin() as conn:
        conn.execute(text(query))


# =====================================================
# SAVE DATASET PROFILE
# =====================================================

def save_dataset_memory(
    user_email,
    dataset_name,
    profile
):

    user_email = str(
        user_email
    ).strip().lower()

    dataset_name = str(
        dataset_name
    ).strip()

    if not user_email:
        raise ValueError(
            "User email is required."
        )

    if not dataset_name:
        raise ValueError(
            "Dataset name is required."
        )

    create_dataset_memory_table()

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
        CAST(:profile AS JSONB)
    )

    ON CONFLICT (
        user_email,
        dataset_name
    )

    DO UPDATE SET

        profile = EXCLUDED.profile,

        created_at = CURRENT_TIMESTAMP;
    """

    with engine.begin() as conn:

        conn.execute(
            text(query),
            {
                "user_email": user_email,
                "dataset_name": dataset_name,
                "profile": json.dumps(
                    profile,
                    default=str
                )
            }
        )


# =====================================================
# GET DATASET MEMORY
# =====================================================

def get_dataset_memory(
    user_email,
    dataset_name
):

    user_email = str(
        user_email
    ).strip().lower()

    dataset_name = str(
        dataset_name
    ).strip()

    create_dataset_memory_table()

    query = """
    SELECT profile

    FROM dataset_memory

    WHERE user_email = :user_email

    AND dataset_name = :dataset_name

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

    if not row:
        return None

    profile = row[0]

    if isinstance(profile, str):

        return json.loads(profile)

    return profile


# =====================================================
# GET ALL USER DATASETS
# =====================================================

def get_user_datasets(user_email):

    user_email = str(
        user_email
    ).strip().lower()

    if not user_email:
        return []

    create_dataset_memory_table()

    query = """
    SELECT
        dataset_name,
        profile,
        created_at

    FROM dataset_memory

    WHERE user_email = :user_email

    ORDER BY created_at DESC;
    """

    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            {
                "user_email": user_email
            }
        )

        rows = result.fetchall()

    datasets = []

    for row in rows:

        profile = row[1]

        if isinstance(profile, str):

            profile = json.loads(profile)

        datasets.append(
            {
                "dataset_name": row[0],
                "profile": profile,
                "created_at": row[2]
            }
        )

    return datasets


# =====================================================
# CHECK DATASET OWNERSHIP
# =====================================================

def user_owns_dataset(
    user_email,
    dataset_name
):

    user_email = str(
        user_email
    ).strip().lower()

    dataset_name = str(
        dataset_name
    ).strip()

    query = """
    SELECT EXISTS (

        SELECT 1

        FROM dataset_memory

        WHERE user_email = :user_email

        AND dataset_name = :dataset_name

    );
    """

    with engine.connect() as conn:

        result = conn.execute(
            text(query),
            {
                "user_email": user_email,
                "dataset_name": dataset_name
            }
        )

        return bool(
            result.scalar()
        )


# =====================================================
# DELETE DATASET MEMORY
# =====================================================

def delete_dataset_memory(
    user_email,
    dataset_name
):

    user_email = str(
        user_email
    ).strip().lower()

    dataset_name = str(
        dataset_name
    ).strip()

    query = """
    DELETE FROM dataset_memory

    WHERE user_email = :user_email

    AND dataset_name = :dataset_name;
    """

    with engine.begin() as conn:

        result = conn.execute(
            text(query),
            {
                "user_email": user_email,
                "dataset_name": dataset_name
            }
        )

    return result.rowcount > 0


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
