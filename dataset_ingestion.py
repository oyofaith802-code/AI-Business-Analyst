import os
import re
import json
import pandas as pd

from dotenv import load_dotenv
from sqlalchemy import text, inspect

from database import engine
from schema_memory import save_existing_table_schema
from dataset_memory import create_dataset_memory_table, save_dataset_memory


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CLEAN EMAIL
# ============================================================

def clean_email(email):
    if not email:
        return ""

    email = str(email).strip()

    # Convert Markdown email format:
    # [name@gmail.com](mailto:name@gmail.com)
    match = re.search(r"\[([^\]]+@[^\]]+)\]", email)

    if match:
        email = match.group(1)

    email = email.replace("mailto:", "")
    email = email.replace("\\", "")

    return email.strip()


# ============================================================
# CLEAN TABLE NAME
# ============================================================

def clean_table_name(filename):
    name = os.path.basename(filename)

    name = os.path.splitext(name)[0]

    name = name.lower()

    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)

    name = re.sub(r"_+", "_", name)

    name = name.strip("_")

    if not name:
        name = "uploaded_dataset"

    if name[0].isdigit():
        name = "dataset_" + name

    return name[:60]


# ============================================================
# LOAD DATASET
# ============================================================

def load_dataset(file_path):

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".csv":

        df = pd.read_csv(file_path)

    elif extension in [".xlsx", ".xls"]:

        df = pd.read_excel(file_path)

    else:

        raise ValueError(
            "Unsupported file format. "
            "Please upload CSV or Excel files."
        )

    return df


# ============================================================
# CLEAN COLUMN NAMES
# ============================================================

def clean_column_names(df):

    df = df.copy()

    cleaned_columns = []

    for column in df.columns:

        column = str(column).strip().lower()

        column = re.sub(
            r"[^a-zA-Z0-9_]",
            "_",
            column
        )

        column = re.sub(
            r"_+",
            "_",
            column
        )

        column = column.strip("_")

        if not column:
            column = "column"

        cleaned_columns.append(column)

    # Prevent duplicate column names
    seen = {}

    final_columns = []

    for column in cleaned_columns:

        if column not in seen:

            seen[column] = 0
            final_columns.append(column)

        else:

            seen[column] += 1

            final_columns.append(
                f"{column}_{seen[column]}"
            )

    df.columns = final_columns

    return df


# ============================================================
# DETECT DATE COLUMNS
# ============================================================

def detect_date_columns(df):

    date_columns = []

    for column in df.columns:

        column_name = column.lower()

        # Strong date-name indicators
        date_keywords = [
            "date",
            "time",
            "timestamp",
            "created_at",
            "updated_at",
            "datetime"
        ]

        looks_like_date = any(
            keyword in column_name
            for keyword in date_keywords
        )

        if not looks_like_date:
            continue

        try:

            converted = pd.to_datetime(
                df[column],
                errors="coerce"
            )

            valid_count = converted.notna().sum()

            total_count = len(df[column])

            if total_count > 0:

                ratio = valid_count / total_count

                if ratio >= 0.5:

                    df[column] = converted

                    date_columns.append(column)

                    print(
                        f"✅ Date detected: {column}"
                    )

        except Exception:

            continue

    return df, date_columns


# ============================================================
# PROFILE DATASET
# ============================================================

def profile_dataset(df, date_columns):

    profile = {

        "rows": int(len(df)),

        "columns": int(len(df.columns)),

        "column_names": [
            str(column)
            for column in df.columns
        ],

        "column_types": {
            column: str(df[column].dtype)
            for column in df.columns
        },

        "date_columns": date_columns,

        "missing_values": {
            column: int(df[column].isna().sum())
            for column in df.columns
        },

        "unique_values": {
            column: int(df[column].nunique())
            for column in df.columns
        },

        "numeric_columns": [
            column
            for column in df.columns
            if pd.api.types.is_numeric_dtype(
                df[column]
            )
        ],

        "text_columns": [
            column
            for column in df.columns
            if pd.api.types.is_object_dtype(
                df[column]
            )
        ]
    }

    return profile


# ============================================================
# SAVE DATASET TO DATABASE
# ============================================================

def save_dataset_to_database(df, table_name):

    print("🗄️ Saving dataset to database...")

    try:

        df.to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False,
            method="multi"
        )

        print(
            f"✅ Dataset saved successfully as table: {table_name}"
        )

    except Exception as e:

        print("\n❌ DATABASE SAVE ERROR")
        print(e)

        raise


# ============================================================
# VERIFY DATABASE TABLE
# ============================================================

def verify_database_table(table_name):

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    if table_name not in tables:

        raise RuntimeError(
            f"Database table '{table_name}' was not created."
        )

    with engine.connect() as conn:

        result = conn.execute(
            text(
                f'SELECT COUNT(*) FROM "{table_name}"'
            )
        )

        row_count = result.scalar()

    print(
        f"📊 Database rows: {row_count}"
    )

    print(
        f"✅ Database table verified: {table_name}"
    )

    return row_count


# ============================================================
# SAVE SCHEMA MEMORY
# ============================================================

def save_schema_memory(
    user_email,
    table_name
):

    print("🧠 Saving schema memory...")

    try:

        success = save_existing_table_schema(
            user_email,
            table_name
        )

        if success:

            print(
                "✅ Schema memory updated."
            )

        else:

            print(
                "⚠️ Schema memory could not be updated."
            )

    except Exception as e:

        print(
            "⚠️ Schema memory update failed:"
        )

        print(e)


# ============================================================
# SAVE DATASET MEMORY
# ============================================================

def save_dataset_memory_data(
    user_email,
    table_name,
    profile
):

    print("🧠 Saving dataset memory...")

    try:

        create_dataset_memory_table()

        save_dataset_memory(
            user_email,
            table_name,
            profile
        )

        print(
            "✅ Dataset memory updated."
        )

    except Exception as e:

        print(
            "⚠️ Dataset memory update failed:"
        )

        print(e)


# ============================================================
# MAIN INGESTION FUNCTION
# ============================================================

def ingest_dataset(
    file_path,
    user_email
):

    user_email = clean_email(
        user_email
    )

    if not user_email:

        raise ValueError(
            "User email cannot be empty."
        )

    print("\n📂 Reading dataset...")

    df = load_dataset(
        file_path
    )

    print(
        f"✅ Dataset loaded: {len(df)} rows"
    )

    print(
        f"📊 Columns detected: {len(df.columns)}"
    )

    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    df = clean_column_names(df)

    # --------------------------------------------------------
    # DATE DETECTION
    # --------------------------------------------------------

    print(
        "📅 Detecting date columns..."
    )

    df, date_columns = detect_date_columns(
        df
    )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    print(
        "🔍 Profiling dataset..."
    )

    profile = profile_dataset(
        df,
        date_columns
    )

    print(
        "✅ Dataset profile created."
    )

    # --------------------------------------------------------
    # TABLE NAME
    # --------------------------------------------------------

    table_name = clean_table_name(
        file_path
    )

    print(
        f"📝 Database table name: {table_name}"
    )

    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    save_dataset_to_database(
        df,
        table_name
    )

    row_count = verify_database_table(
        table_name
    )

    # --------------------------------------------------------
    # SCHEMA MEMORY
    # --------------------------------------------------------

    save_schema_memory(
        user_email,
        table_name
    )

    # --------------------------------------------------------
    # DATASET MEMORY
    # --------------------------------------------------------

    save_dataset_memory_data(
        user_email,
        table_name,
        profile
    )

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    print("\n" + "=" * 60)

    print(
        "DATASET INGESTION COMPLETE"
    )

    print("=" * 60)

    print(
        f"Dataset: {table_name}"
    )

    print(
        f"Rows: {row_count}"
    )

    print(
        f"Columns: {len(df.columns)}"
    )

    print(
        f"Date columns: {len(date_columns)}"
    )

    print(
        "\n🧠 The dataset is now available "
        "for AI business analysis."
    )

    return {
        "table_name": table_name,
        "rows": row_count,
        "columns": len(df.columns),
        "date_columns": date_columns,
        "profile": profile
    }


# ============================================================
# COMMAND LINE
# ============================================================

def main():

    print("\n" + "=" * 60)

    print(
        "🤖 AI BUSINESS ANALYST - DYNAMIC DATASET LOADER"
    )

    print("=" * 60)

    file_path = input(
        "\nEnter CSV/Excel file path: "
    ).strip()

    user_email = input(
        "Enter user email: "
    ).strip()

    user_email = clean_email(
        user_email
    )

    if not file_path:

        print(
            "\n❌ File path cannot be empty."
        )

        return

    if not user_email:

        print(
            "\n❌ Email cannot be empty."
        )

        return

    try:

        ingest_dataset(
            file_path,
            user_email
        )

    except Exception as e:

        print(
            "\n❌ DATASET INGESTION FAILED"
        )

        print(e)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    main()