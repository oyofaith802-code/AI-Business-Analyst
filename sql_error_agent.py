# ============================================================
# AI BUSINESS ANALYST
# SQL ERROR REPAIR AGENT
# ============================================================

import re

from ollama import chat

from schema_memory import get_schema


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(response):

    if response is None:
        return ""

    sql = str(response).strip()

    # Remove markdown code fences
    sql = re.sub(
        r"```sql",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"```",
        "",
        sql
    )

    sql = sql.strip()

    # Find SELECT or WITH
    match = re.search(
        r"\b(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE
    )

    if match:
        sql = sql[match.start():]

    # Remove trailing semicolon
    sql = sql.strip()

    return sql


# ============================================================
# BASIC SQL SAFETY CHECK
# ============================================================

def is_safe_sql(sql):

    if not sql:
        return False

    sql_upper = sql.strip().upper()

    # Only SELECT / WITH queries are allowed
    if not (
        sql_upper.startswith("SELECT")
        or sql_upper.startswith("WITH")
    ):
        return False

    # Block destructive SQL
    forbidden = [
        "DROP ",
        "DELETE ",
        "TRUNCATE ",
        "ALTER ",
        "UPDATE ",
        "INSERT ",
        "CREATE ",
        "GRANT ",
        "REVOKE "
    ]

    for keyword in forbidden:

        if keyword in sql_upper:
            return False

    return True


# ============================================================
# REPAIR SQL
# ============================================================

def repair_sql(
    sql,
    error_message,
    tables,
    user_email=None
):

    # --------------------------------------------------------
    # GET DATABASE SCHEMA
    # --------------------------------------------------------

    schema = get_schema(
        user_email,
        tables
    )

    if not schema:

        raise ValueError(
            "No database schema available for SQL repair."
        )

    # --------------------------------------------------------
    # BUILD REPAIR PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are an expert PostgreSQL SQL repair agent.

A previous AI-generated SQL query failed when executed.

DATABASE SCHEMA:

{schema}

ORIGINAL SQL:

{sql}

POSTGRESQL ERROR:

{error_message}

Your task is to fix the SQL query.

IMPORTANT RULES:

1. Return ONLY the corrected SQL.
2. Do not explain anything.
3. Do not use markdown.
4. Return exactly ONE query.
5. The query must be SELECT or WITH.
6. Do not invent tables.
7. Do not invent columns.
8. Use only columns from the provided schema.
9. Use valid PostgreSQL syntax.
10. Do not modify the database.
11. Do not use INSERT.
12. Do not use UPDATE.
13. Do not use DELETE.
14. Do not use DROP.
15. Do not use ALTER.
16. Do not use TRUNCATE.
17. Preserve the original business question implied by the SQL.
18. Fix only the problem causing the SQL error.

Return the corrected SQL now.
"""

    # --------------------------------------------------------
    # CALL OLLAMA
    # --------------------------------------------------------

    response = chat(

        model="llama3.2",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],

        options={
            "temperature": 0
        }
    )

    # --------------------------------------------------------
    # EXTRACT RESPONSE
    # --------------------------------------------------------

    raw_response = response[
        "message"
    ][
        "content"
    ]

    # --------------------------------------------------------
    # CLEAN RESPONSE
    # --------------------------------------------------------

    repaired_sql = clean_sql(
        raw_response
    )

    # --------------------------------------------------------
    # VALIDATE RESPONSE
    # --------------------------------------------------------

    if not repaired_sql:

        raise ValueError(
            "AI returned an empty repaired SQL query."
        )

    if not re.match(
        r"^(SELECT|WITH)\b",
        repaired_sql,
        flags=re.IGNORECASE
    ):

        raise ValueError(
            "AI returned an invalid repaired SQL query."
        )

    if not is_safe_sql(
        repaired_sql
    ):

        raise ValueError(
            "AI returned unsafe SQL."
        )

    return repaired_sql


# ============================================================
# AUTO REPAIR
# ============================================================

def fix_sql_error(
    sql,
    error_message,
    tables,
    user_email=None
):

    print(
        "🔧 Attempting to repair SQL..."
    )

    repaired_sql = repair_sql(
        sql=sql,
        error_message=error_message,
        tables=tables,
        user_email=user_email
    )

    print(
        "✅ SQL repaired."
    )

    return repaired_sql


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================================"
    )

    print(
        "SQL ERROR REPAIR AGENT TEST"
    )

    print(
        "============================================================"
    )

    email = input(
        "Enter user email: "
    ).strip()

    dataset = input(
        "Enter dataset name: "
    ).strip()

    tables = [
        dataset
    ]

    # --------------------------------------------------------
    # Deliberately broken SQL
    # --------------------------------------------------------

    broken_sql = """
    SELECT
        category,
        SUM(revenue) AS total_revenue
    FROM test_sales
    GROUP BY category
    ORDER BY total_sales DESC;
    """

    error_message = (
        'column "total_sales" does not exist'
    )

    print()
    print(
        "Original SQL:"
    )

    print(
        broken_sql
    )

    print()
    print(
        "PostgreSQL error:"
    )

    print(
        error_message
    )

    print()
    print(
        "Repairing..."
    )

    try:

        repaired = fix_sql_error(
            sql=broken_sql,
            error_message=error_message,
            tables=tables,
            user_email=email
        )

        print()
        print(
            "Corrected SQL:"
        )

        print(
            repaired
        )

        print()
        print(
            "============================================================"
        )

        print(
            "✅ SQL REPAIR TEST COMPLETED"
        )

        print(
            "============================================================"
        )

    except Exception as e:

        print()
        print(
            "❌ SQL repair failed:"
        )

        print(
            e
        )
