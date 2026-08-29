import re

from database import engine
from sqlalchemy import inspect


# ============================================================
# GET ALL DATABASE TABLES
# ============================================================

def get_database_tables():

    inspector = inspect(engine)

    try:

        tables = inspector.get_table_names()

        return set(tables)

    except Exception:

        return set()


# ============================================================
# GET TABLE COLUMNS
# ============================================================

def get_table_columns(table_name):

    inspector = inspect(engine)

    try:

        columns = inspector.get_columns(
            table_name
        )

        return {
            column["name"]
            for column in columns
        }

    except Exception:

        return set()


# ============================================================
# EXTRACT TABLES FROM SQL
# ============================================================

def extract_tables(sql):

    tables = []

    # FROM table
    from_matches = re.findall(
        r"\bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE
    )

    # JOIN table
    join_matches = re.findall(
        r"\bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE
    )

    tables.extend(from_matches)
    tables.extend(join_matches)

    # Remove duplicates
    tables = list(
        dict.fromkeys(tables)
    )

    return tables


# ============================================================
# EXTRACT COLUMNS FROM SQL
# ============================================================

def extract_columns(sql):

    columns = []

    # Detect table.column
    qualified_columns = re.findall(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)\b",
        sql
    )

    for table, column in qualified_columns:

        columns.append(
            f"{table}.{column}"
        )

    # Detect common SQL functions
    function_columns = re.findall(
        r"\b(?:SUM|AVG|COUNT|MIN|MAX)\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\)",
        sql,
        re.IGNORECASE
    )

    columns.extend(
        function_columns
    )

    return list(
        dict.fromkeys(columns)
    )


# ============================================================
# VALIDATE SQL
# ============================================================

def validate_sql(sql):

    result = {
        "valid": True,
        "errors": [],
        "tables": [],
        "columns": []
    }

    if not sql:

        result["valid"] = False

        result["errors"].append(
            "SQL query is empty."
        )

        return result

    sql = sql.strip()

    # ========================================================
    # BASIC SECURITY
    # ========================================================

    forbidden = [
        "DROP",
        "DELETE",
        "TRUNCATE",
        "ALTER",
        "CREATE",
        "INSERT",
        "UPDATE",
        "GRANT",
        "REVOKE"
    ]

    sql_upper = sql.upper()

    for keyword in forbidden:

        pattern = rf"\b{keyword}\b"

        if re.search(
            pattern,
            sql_upper
        ):

            result["valid"] = False

            result["errors"].append(
                f"Forbidden SQL operation: {keyword}"
            )

    if not re.match(
        r"^\s*SELECT\b",
        sql,
        re.IGNORECASE
    ):

        result["valid"] = False

        result["errors"].append(
            "Only SELECT queries are allowed."
        )

        return result

    # ========================================================
    # GET DATABASE TABLES
    # ========================================================

    database_tables = get_database_tables()

    # ========================================================
    # EXTRACT TABLES
    # ========================================================

    tables = extract_tables(
        sql
    )

    result["tables"] = tables

    if not tables:

        result["valid"] = False

        result["errors"].append(
            "No database table detected in SQL."
        )

        return result

    # ========================================================
    # VALIDATE TABLES
    # ========================================================

    for table in tables:

        if table not in database_tables:

            result["valid"] = False

            result["errors"].append(
                f"Table does not exist: {table}"
            )

    # ========================================================
    # EXTRACT COLUMNS
    # ========================================================

    columns = extract_columns(
        sql
    )

    result["columns"] = columns

    # ========================================================
    # VALIDATE QUALIFIED COLUMNS
    # ========================================================

    for qualified_column in columns:

        if "." not in qualified_column:

            continue

        table_name, column_name = (
            qualified_column.split(
                ".",
                1
            )
        )

        if table_name not in database_tables:

            continue

        table_columns = get_table_columns(
            table_name
        )

        if column_name not in table_columns:

            result["valid"] = False

            result["errors"].append(
                f"Column does not exist: "
                f"{table_name}.{column_name}"
            )

    # ========================================================
    # VALIDATE UNQUALIFIED COLUMNS
    # ========================================================

    unqualified_columns = [
        column
        for column in columns
        if "." not in column
    ]

    if len(tables) == 1:

        table_name = tables[0]

        table_columns = get_table_columns(
            table_name
        )

        for column in unqualified_columns:

            if column not in table_columns:

                result["valid"] = False

                result["errors"].append(
                    f"Column does not exist: "
                    f"{table_name}.{column}"
                )

    # ========================================================
    # REMOVE DUPLICATE ERRORS
    # ========================================================

    result["errors"] = list(
        dict.fromkeys(
            result["errors"]
        )
    )

    return result


# ============================================================
# COMMAND LINE TEST
# ============================================================

def main():

    print("=" * 60)
    print("SQL VALIDATOR TEST")
    print("=" * 60)

    sql = input(
        "\nEnter SQL query: "
    ).strip()

    validation = validate_sql(
        sql
    )

    print(
        "\nVALID:",
        validation["valid"]
    )

    print(
        "\nTABLES:"
    )

    for table in validation["tables"]:

        print(
            f"• {table}"
        )

    print(
        "\nCOLUMNS:"
    )

    for column in validation["columns"]:

        print(
            f"• {column}"
        )

    if validation["errors"]:

        print(
            "\nERRORS:"
        )

        for error in validation["errors"]:

            print(
                f"• {error}"
            )

    else:

        print(
            "\n✅ SQL validation passed."
        )


if __name__ == "__main__":

    main()