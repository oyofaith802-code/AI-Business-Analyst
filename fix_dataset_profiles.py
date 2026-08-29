from database import engine
from sqlalchemy import text


def fix_dataset_profiles():

    print("=" * 60)
    print("FIXING dataset_profiles TABLE")
    print("=" * 60)

    with engine.begin() as conn:

        # --------------------------------------------------
        # CHECK CURRENT COLUMNS
        # --------------------------------------------------

        print("\nChecking current table structure...")

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'dataset_profiles'
                ORDER BY ordinal_position
            """)
        )

        columns = result.fetchall()

        if columns:

            print("\nCurrent columns:")

            for column in columns:
                print(f"• {column[0]} : {column[1]}")

        else:

            print("\nTable does not exist.")

        # --------------------------------------------------
        # CREATE TABLE IF IT DOES NOT EXIST
        # --------------------------------------------------

        conn.execute(
            text("""
                CREATE TABLE IF NOT EXISTS dataset_profiles (
                    id SERIAL PRIMARY KEY,
                    user_email TEXT NOT NULL,
                    dataset_name TEXT NOT NULL,
                    profile JSONB NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
        )

        # --------------------------------------------------
        # ADD MISSING COLUMNS
        # --------------------------------------------------

        conn.execute(
            text("""
                ALTER TABLE dataset_profiles
                ADD COLUMN IF NOT EXISTS user_email TEXT
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE dataset_profiles
                ADD COLUMN IF NOT EXISTS dataset_name TEXT
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE dataset_profiles
                ADD COLUMN IF NOT EXISTS profile JSONB
            """)
        )

        conn.execute(
            text("""
                ALTER TABLE dataset_profiles
                ADD COLUMN IF NOT EXISTS created_at
                TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            """)
        )

        # --------------------------------------------------
        # FIX NULL VALUES
        # --------------------------------------------------

        conn.execute(
            text("""
                UPDATE dataset_profiles
                SET created_at = CURRENT_TIMESTAMP
                WHERE created_at IS NULL
            """)
        )

        # --------------------------------------------------
        # CREATE UNIQUE INDEX
        # --------------------------------------------------

        conn.execute(
            text("""
                CREATE UNIQUE INDEX IF NOT EXISTS
                dataset_profiles_user_dataset_unique
                ON dataset_profiles (
                    user_email,
                    dataset_name
                )
            """)
        )

        # --------------------------------------------------
        # FINAL CHECK
        # --------------------------------------------------

        print("\nFinal table structure:")

        result = conn.execute(
            text("""
                SELECT
                    column_name,
                    data_type
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'dataset_profiles'
                ORDER BY ordinal_position
            """)
        )

        for column in result.fetchall():

            print(
                f"• {column[0]} : {column[1]}"
            )

    print("\n" + "=" * 60)
    print("✅ dataset_profiles FIX COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    fix_dataset_profiles()