# ============================================================
# AI BUSINESS ANALYST - DATASET MANAGEMENT
# ============================================================

import re

from sqlalchemy import text

from database import engine
from dataset_profile_storage import (
    get_user_dataset_profiles,
)


# ============================================================
# CLEAN IDENTIFIER
# ============================================================

def clean_identifier(value):

    value = str(value).strip()

    if not re.match(
        r"^[a-zA-Z0-9_]+$",
        value
    ):
        raise ValueError(
            "Invalid dataset name."
        )

    return value


# ============================================================
# GET USER DATASETS
# ============================================================

def get_user_datasets(user_email):

    if not user_email:
        return []

    try:

        profiles = get_user_dataset_profiles(
            user_email
        )

        return [
            item["dataset_name"]
            for item in profiles
            if item.get("dataset_name")
        ]

    except Exception as e:

        print(
            f"Could not load datasets: {e}"
        )

        return []


# ============================================================
# CHECK DATASET OWNERSHIP
# ============================================================

def user_owns_dataset(
    user_email,
    dataset_name
):

    datasets = get_user_datasets(
        user_email
    )

    return dataset_name in datasets


# ============================================================
# GET DATASET STATISTICS
# ============================================================

def get_dataset_statistics(
    user_email,
    dataset_name
):

    dataset_name = clean_identifier(
        dataset_name
    )

    if not user_owns_dataset(
        user_email,
        dataset_name
    ):

        return None


    try:

        query = text(
            f'''
            SELECT
                COUNT(*) AS rows
            FROM "{dataset_name}"
            '''
        )

        with engine.connect() as conn:

            row = conn.execute(
                query
            ).fetchone()


        profile = None

        profiles = get_user_dataset_profiles(
            user_email
        )

        for item in profiles:

            if item.get(
                "dataset_name"
            ) == dataset_name:

                profile = item.get(
                    "profile",
                    {}
                )

                break


        return {

            "dataset_name":
                dataset_name,

            "rows":
                int(row.rows),

            "columns":
                int(
                    profile.get(
                        "columns",
                        0
                    )
                ),

            "column_names":
                profile.get(
                    "column_names",
                    []
                )

        }

    except Exception as e:

        print(
            f"Could not get dataset statistics: {e}"
        )

        return None


# ============================================================
# DELETE DATASET
# ============================================================

def delete_dataset(
    user_email,
    dataset_name
):

    dataset_name = clean_identifier(
        dataset_name
    )


    # --------------------------------------------------------
    # SECURITY CHECK
    # --------------------------------------------------------

    if not user_owns_dataset(
        user_email,
        dataset_name
    ):

        return {
            "success": False,
            "error": "You do not own this dataset."
        }


    try:

        # ----------------------------------------------------
        # DROP DATABASE TABLE
        # ----------------------------------------------------

        query = text(
            f'''
            DROP TABLE IF EXISTS
            "{dataset_name}"
            '''
        )

        with engine.begin() as conn:

            conn.execute(
                query
            )


        # ----------------------------------------------------
        # DELETE PROFILE
        # ----------------------------------------------------

        profile_query = text(
            """
            DELETE FROM dataset_profiles

            WHERE user_email = :user_email

            AND dataset_name = :dataset_name
            """
        )


        with engine.begin() as conn:

            result = conn.execute(
                profile_query,
                {
                    "user_email":
                        user_email.strip().lower(),

                    "dataset_name":
                        dataset_name
                }
            )


        if result.rowcount == 0:

            return {
                "success": False,
                "error": "Dataset profile was not found."
            }


        return {
            "success": True,
            "message":
                f"Dataset '{dataset_name}' deleted successfully."
        }


    except Exception as e:

        return {
            "success": False,
            "error":
                f"Could not delete dataset: {e}"
        }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)

    print(
        "AI BUSINESS ANALYST - DATASET MANAGEMENT"
    )

    print("=" * 60)

    print()

    print(
        "Dataset management module loaded successfully."
    )

    print()

    print(
        "Available functions:"
    )

    print(
        "• get_user_datasets()"
    )

    print(
        "• user_owns_dataset()"
    )

    print(
        "• get_dataset_statistics()"
    )

    print(
        "• delete_dataset()"
    )