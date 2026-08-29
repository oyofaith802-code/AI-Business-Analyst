from database import engine
from sqlalchemy import inspect, text
import re


BUSINESS_TABLES = [
    "products",
    "order_items",
    "orders",
    "payments",
    "customers",
    "reviews"
]


def clean_email(email):

    if not email:
        return ""

    email = str(email).strip()

    match = re.search(
        r"\[([^\]]+@[^\]]+)\]",
        email
    )

    if match:
        email = match.group(1)

    email = email.replace("mailto:", "")
    email = email.replace("\\", "")
    email = email.strip()

    return email


def create_schema_table():

    with engine.begin() as conn:

        conn.execute(
            text("""
                CREATE TABLE IF NOT EXISTS schema_memory (

                    id SERIAL PRIMARY KEY,

                    user_email TEXT NOT NULL,

                    table_name TEXT NOT NULL,

                    columns TEXT NOT NULL

                )
            """)
        )


def save_schema(
    user_email,
    table_name,
    columns
):

    create_schema_table()

    user_email = clean_email(user_email)

    with engine.begin() as conn:

        conn.execute(
            text("""
                DELETE FROM schema_memory

                WHERE user_email = :user_email

                AND table_name = :table_name
            """),
            {
                "user_email": user_email,
                "table_name": table_name
            }
        )

        conn.execute(
            text("""
                INSERT INTO schema_memory
                (
                    user_email,
                    table_name,
                    columns
                )

                VALUES
                (
                    :user_email,
                    :table_name,
                    :columns
                )
            """),
            {
                "user_email": user_email,
                "table_name": table_name,
                "columns": columns
            }
        )


def save_existing_table_schema(
    user_email,
    table_name
):

    create_schema_table()

    user_email = clean_email(user_email)

    inspector = inspect(engine)

    try:

        columns = inspector.get_columns(
            table_name
        )

    except Exception:

        return False

    if not columns:

        return False

    schema_lines = []

    for column in columns:

        column_name = column["name"]

        column_type = str(
            column["type"]
        )

        schema_lines.append(
            f"{column_name} : {column_type}"
        )

    schema_text = "\n".join(
        schema_lines
    )

    save_schema(
        user_email,
        table_name,
        schema_text
    )

    return True


def save_all_existing_table_schemas(
    user_email
):

    create_schema_table()

    saved = []

    for table_name in BUSINESS_TABLES:

        try:

            success = save_existing_table_schema(
                user_email,
                table_name
            )

            if success:

                saved.append(
                    table_name
                )

        except Exception:

            continue

    return saved


def get_table_schema(
    user_email,
    table_name
):

    create_schema_table()

    user_email = clean_email(user_email)

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT columns

                    FROM schema_memory

                    WHERE user_email = :user_email

                    AND table_name = :table_name

                    ORDER BY id DESC

                    LIMIT 1
                """),
                {
                    "user_email": user_email,
                    "table_name": table_name
                }
            )

            row = result.fetchone()

            if row and row[0]:

                return str(row[0])

    except Exception:

        pass

    inspector = inspect(engine)

    try:

        columns = inspector.get_columns(
            table_name
        )

    except Exception:

        return ""

    if not columns:

        return ""

    schema_lines = []

    for column in columns:

        column_name = column["name"]

        column_type = str(
            column["type"]
        )

        schema_lines.append(
            f"{column_name} : {column_type}"
        )

    schema_text = "\n".join(
        schema_lines
    )

    try:

        save_schema(
            user_email,
            table_name,
            schema_text
        )

    except Exception:

        pass

    return schema_text


def get_schema(
    user_email,
    tables=None
):

    create_schema_table()

    user_email = clean_email(user_email)

    if not tables:

        tables = BUSINESS_TABLES

    schema_blocks = []

    for table_name in tables:

        schema_text = get_table_schema(
            user_email,
            table_name
        )

        if not schema_text:

            continue

        schema_blocks.append(
            f"TABLE: {table_name}\n\n"
            f"COLUMNS:\n\n"
            f"{schema_text}"
        )

    return "\n\n---\n\n".join(
        schema_blocks
    )


def get_business_tables():

    return BUSINESS_TABLES.copy()


def is_business_table(
    table_name
):

    return table_name in BUSINESS_TABLES