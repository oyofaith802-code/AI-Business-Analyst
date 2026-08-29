from database import engine
from sqlalchemy import text
import json


# ============================================================
# GET DATASET PROFILE
# ============================================================

def get_dataset_profile(user_email, dataset_name):

    sql = text("""
        SELECT
            profile
        FROM dataset_profiles
        WHERE user_email = :user_email
        AND dataset_name = :dataset_name
        LIMIT 1
    """)

    try:

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

            # PostgreSQL JSONB may already be a dict
            if isinstance(profile, dict):
                return profile

            # Otherwise convert JSON text
            if isinstance(profile, str):
                return json.loads(profile)

            return profile

    except Exception as e:

        print("\n❌ PROFILE MEMORY ERROR:")
        print(e)

        return None


# ============================================================
# GET ALL USER DATASET PROFILES
# ============================================================

def get_user_dataset_profiles(user_email):

    sql = text("""
        SELECT
            dataset_name,
            profile
        FROM dataset_profiles
        WHERE user_email = :user_email
        ORDER BY created_at DESC
    """)

    try:

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

                if isinstance(profile, str):
                    profile = json.loads(profile)

                profiles.append(
                    {
                        "dataset_name": row[0],
                        "profile": profile
                    }
                )

            return profiles

    except Exception as e:

        print("\n❌ USER PROFILE ERROR:")
        print(e)

        return []


# ============================================================
# FORMAT PROFILE FOR AI
# ============================================================

def format_profile_for_ai(
    user_email,
    dataset_name
):

    profile = get_dataset_profile(
        user_email,
        dataset_name
    )

    if not profile:

        return None

    lines = []

    lines.append(
        f"Dataset: {dataset_name}"
    )

    lines.append(
        f"Rows: {profile.get('rows', 'Unknown')}"
    )

    lines.append(
        f"Columns: {profile.get('columns', 'Unknown')}"
    )

    column_names = profile.get(
        "column_names",
        []
    )

    if column_names:

        lines.append(
            "\nColumns:"
        )

        for column in column_names:

            lines.append(
                f"- {column}"
            )

    column_profiles = profile.get(
        "column_profiles",
        []
    )

    if column_profiles:

        lines.append(
            "\nColumn details:"
        )

        for column in column_profiles:

            if isinstance(column, dict):

                name = column.get(
                    "column",
                    "Unknown"
                )

                dtype = column.get(
                    "dtype",
                    "Unknown"
                )

                lines.append(
                    f"- {name}: {dtype}"
                )

    statistics = profile.get(
        "statistics",
        {}
    )

    if statistics:

        lines.append(
            "\nStatistics:"
        )

        for column, stats in statistics.items():

            lines.append(
                f"- {column}: {stats}"
            )

    return "\n".join(lines)


# ============================================================
# TEST
# ============================================================

def main():

    print("=" * 60)
    print("DATASET PROFILE MEMORY TEST")
    print("=" * 60)

    email = input(
        "\nEnter user email: "
    ).strip()

    dataset = input(
        "Enter dataset name: "
    ).strip()

    print(
        "\n🧠 Reading saved dataset profile..."
    )

    profile = get_dataset_profile(
        email,
        dataset
    )

    if not profile:

        print(
            "\n❌ No profile found."
        )

        return

    print(
        "\n✅ Profile found."
    )

    print(
        "\n📊 PROFILE:"
    )

    print(
        json.dumps(
            profile,
            indent=2,
            default=str
        )
    )

    print(
        "\n🧠 AI FORMAT:"
    )

    formatted = format_profile_for_ai(
        email,
        dataset
    )

    print(formatted)


if __name__ == "__main__":
    main()