from database import engine
from sqlalchemy import text, inspect
import re


# ============================================================
# CREATE RELATIONSHIP TABLE
# ============================================================

def create_relationship_table():

    sql = """
    CREATE TABLE IF NOT EXISTS relationship_memory (
        id SERIAL PRIMARY KEY,
        user_email TEXT,
        source_table TEXT,
        source_column TEXT,
        target_table TEXT,
        target_column TEXT,
        relationship_type TEXT
    )
    """

    with engine.begin() as conn:
        conn.execute(text(sql))


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column(column):

    column = str(column).lower().strip()

    column = column.replace("-", "_")
    column = column.replace(" ", "_")

    return column


# ============================================================
# COLUMN SIMILARITY
# ============================================================

def columns_match(column1, column2):

    c1 = normalize_column(column1)
    c2 = normalize_column(column2)

    # Exact match
    if c1 == c2:
        return True

    # Example:
    # customer_id ↔ customer_id
    # order_id ↔ order_id

    return False


# ============================================================
# GET TABLE COLUMNS
# ============================================================

def get_table_columns(table_name):

    inspector = inspect(engine)

    try:

        columns = inspector.get_columns(table_name)

        return [
            column["name"]
            for column in columns
        ]

    except Exception:

        return []


# ============================================================
# DETECT POSSIBLE RELATIONSHIPS
# ============================================================

def detect_relationships(
    user_email,
    tables
):

    if not tables:

        return []


    relationships = []


    # --------------------------------------------------------
    # Compare every table with every other table
    # --------------------------------------------------------

    for i in range(len(tables)):

        source_table = tables[i]

        source_columns = get_table_columns(
            source_table
        )


        for j in range(len(tables)):

            if i == j:

                continue


            target_table = tables[j]

            target_columns = get_table_columns(
                target_table
            )


            for source_column in source_columns:

                for target_column in target_columns:

                    if not columns_match(
                        source_column,
                        target_column
                    ):

                        continue


                    column = normalize_column(
                        source_column
                    )


                    # ------------------------------------------------
                    # Only consider likely relationship columns
                    # ------------------------------------------------

                    relationship_words = [

                        "id",
                        "_id"

                    ]


                    is_identifier = (
                        column == "id"
                        or column.endswith("_id")
                        or column.endswith("id")
                    )


                    if not is_identifier:

                        continue


                    relationship = {

                        "source_table": source_table,

                        "source_column": source_column,

                        "target_table": target_table,

                        "target_column": target_column,

                        "relationship_type": "shared_identifier"

                    }


                    # Avoid duplicates
                    if relationship not in relationships:

                        relationships.append(
                            relationship
                        )


    # ========================================================
    # SAVE RELATIONSHIPS
    # ========================================================

    with engine.begin() as conn:

        # Remove previous relationships
        # for this user's selected tables

        for table in tables:

            conn.execute(
                text("""
                    DELETE FROM relationship_memory
                    WHERE user_email = :user_email
                    AND (
                        source_table = :table
                        OR target_table = :table
                    )
                """),
                {
                    "user_email": user_email,
                    "table": table
                }
            )


        # Save new relationships

        for relationship in relationships:

            conn.execute(
                text("""
                    INSERT INTO relationship_memory (
                        user_email,
                        source_table,
                        source_column,
                        target_table,
                        target_column,
                        relationship_type
                    )
                    VALUES (
                        :user_email,
                        :source_table,
                        :source_column,
                        :target_table,
                        :target_column,
                        :relationship_type
                    )
                """),
                {
                    "user_email": user_email,

                    "source_table":
                        relationship["source_table"],

                    "source_column":
                        relationship["source_column"],

                    "target_table":
                        relationship["target_table"],

                    "target_column":
                        relationship["target_column"],

                    "relationship_type":
                        relationship["relationship_type"]
                }
            )


    return relationships


# ============================================================
# GET RELATIONSHIP SCHEMA
# ============================================================

def get_relationship_schema(
    user_email,
    tables
):

    if not tables:

        return ""


    relationships = []


    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT
                    source_table,
                    source_column,
                    target_table,
                    target_column,
                    relationship_type
                FROM relationship_memory
                WHERE user_email = :user_email
            """),
            {
                "user_email": user_email
            }
        )


        for row in result:

            source_table = row[0]
            source_column = row[1]
            target_table = row[2]
            target_column = row[3]
            relationship_type = row[4]


            # Only return relationships
            # involving selected tables

            if (
                source_table not in tables
                and target_table not in tables
            ):

                continue


            relationships.append(
                f"{source_table}.{source_column} "
                f"→ "
                f"{target_table}.{target_column} "
                f"({relationship_type})"
            )


    if not relationships:

        return ""


    return "\n".join(
        relationships
    )