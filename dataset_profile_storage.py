# ============================================================
# DATASET PROFILE STORAGE
# ============================================================

import json

from sqlalchemy import text

from database import engine

from schema_memory import clean_email


# ============================================================
# CREATE TABLE
# ============================================================

def create_dataset_profiles_table():

    sql = text("""
        CREATE TABLE IF NOT EXISTS dataset_profiles (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            dataset_name TEXT NOT NULL,
            profile JSONB NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_email, dataset_name)
        )
    """)

    with engine.begin() as conn:

        conn.execute(sql)


# ============================================================
# SAVE PROFILE
# ============================================================

def save_dataset_profile(
    user_email,
    dataset_name,
    profile
):

    user_email = clean_email(
        user_email
    )

    create_dataset_profiles_table()

    profile_json = json.dumps(
        profile,
        default=str
    )

    sql = text("""
        INSERT INTO dataset_profiles (
            user_email,
            dataset_name,
            profile
        )
        VALUES (
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
            created_at = CURRENT_TIMESTAMP
    """)

    with engine.begin() as conn:

        conn.execute(
            sql,
            {
                "user_email": user_email,
                "dataset_name": dataset_name,
                "profile": profile_json
            }
        )

    print(
        "✅ Dataset profile saved."
    )


# ============================================================
# GET PROFILE
# ============================================================

def get_dataset_profile(
    user_email,
    dataset_name
):

    user_email = clean_email(
        user_email
    )

    sql = text("""
        SELECT profile
        FROM dataset_profiles
        WHERE user_email = :user_email
        AND dataset_name = :dataset_name
        LIMIT 1
    """)

    with engine.connect() as conn:

        result = conn.execute(
            sql,
            {
                "user_email": user_email,
                "dataset_name": dataset_name
            }
        )

        row = result.fetchone()


    if not row:

        return None


    profile = row[0]


    if isinstance(
        profile,
        str
    ):

        return json.loads(
            profile
        )


    return profile


# ============================================================
# GET ALL USER PROFILES
# ============================================================

def get_user_dataset_profiles(
    user_email
):

    user_email = clean_email(
        user_email
    )

    sql = text("""
        SELECT
            dataset_name,
            profile,
            created_at

        FROM dataset_profiles

        WHERE user_email = :user_email

        ORDER BY created_at DESC
    """)

    with engine.connect() as conn:

        result = conn.execute(
            sql,
            {
                "user_email": user_email
            }
        )

        rows = result.fetchall()


    profiles = []


    for row in rows:

        profile = row[1]

        if isinstance(
            profile,
            str
        ):

            profile = json.loads(
                profile
            )


        profiles.append({

            "dataset_name":
                row[0],

            "profile":
                profile,

            "created_at":
                row[2]

        })


    return profiles


# ============================================================
# DELETE PROFILE
# ============================================================

def delete_dataset_profile(
    user_email,
    dataset_name
):

    user_email = clean_email(
        user_email
    )

    sql = text("""
        DELETE FROM dataset_profiles

        WHERE user_email = :user_email
        AND dataset_name = :dataset_name
    """)

    with engine.begin() as conn:

        result = conn.execute(
            sql,
            {
                "user_email": user_email,
                "dataset_name": dataset_name
            }
        )


    if result.rowcount > 0:

        print(
            "✅ Dataset profile deleted."
        )

        return True


    print(
        "⚠️ Dataset profile not found."
    )

    return False


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Creating dataset_profiles table..."
    )

    create_dataset_profiles_table()

    print(
        "✅ dataset_profiles table ready."
    )