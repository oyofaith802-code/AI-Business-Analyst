from llm import ask_ai
from schema_memory import get_schema


def fix_sql_error(sql, error, tables, user_id):

    schema = get_schema(
        user_id,
        tables
    )

    prompt = f"""
You are a PostgreSQL SQL debugging expert.

DATABASE SCHEMA:
{schema}

ORIGINAL SQL:
{sql}

DATABASE ERROR:
{error}

Fix the SQL ONLY if the requested question can actually
be answered using the provided schema.

IMPORTANT:

1. Use only existing tables.
2. Use only existing columns.
3. Respect PostgreSQL data types.
4. Never invent columns.
5. Never invent revenue, sales, profit, customer or order fields.
6. Do not change the meaning of the user's question.
7. If the question cannot be answered from the schema,
   return exactly:

NOT_ANSWERABLE

8. If it can be fixed, return ONLY valid PostgreSQL SQL.
9. Do not explain anything.
10. Do not use Markdown.
11. Do not use ```sql.
"""

    fixed = ask_ai(prompt)

    fixed = fixed.strip()

    if "```sql" in fixed:
        fixed = fixed.replace("```sql", "")

    if "```" in fixed:
        fixed = fixed.replace("```", "")

    fixed = fixed.strip()

    if "NOT_ANSWERABLE" in fixed.upper():
        return "NOT_ANSWERABLE"

    if not fixed.upper().startswith(
        ("SELECT", "WITH")
    ):
        return "NOT_ANSWERABLE"

    return fixed