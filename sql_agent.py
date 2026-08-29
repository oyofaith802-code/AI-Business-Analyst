# ============================================================
# AI BUSINESS ANALYST
# SQL GENERATION AGENT WITH CHAT MEMORY
# ============================================================

import re

from ollama import chat

from schema_memory import get_schema

from chat_memory import (
    build_memory_context,
)


# ============================================================
# CLEAN SQL RESPONSE
# ============================================================

def clean_sql(response):

    if response is None:
        return ""

    sql = str(response).strip()

    # --------------------------------------------------------
    # Remove markdown code fences
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Find SELECT or WITH
    # --------------------------------------------------------

    match = re.search(
        r"\b(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE
    )

    if match:

        sql = sql[
            match.start():
        ]

    # --------------------------------------------------------
    # Remove trailing semicolon
    # --------------------------------------------------------

    sql = sql.strip()

    if sql.endswith(";"):

        sql = sql[:-1]

    return sql.strip()


# ============================================================
# BUILD MEMORY
# ============================================================

def get_conversation_memory(
    user_email,
    dataset_name,
    question
):

    try:

        memory = build_memory_context(

            user_email=user_email,

            dataset_name=dataset_name,

            current_question=question,

            limit=10
        )

        return memory

    except Exception as e:

        print(
            f"⚠️ Could not load conversation memory: {e}"
        )

        return ""


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(
    question,
    tables,
    user_email=None
):

    # ========================================================
    # VALIDATE INPUT
    # ========================================================

    if not question:

        raise ValueError(
            "Business question is required."
        )

    if not tables:

        raise ValueError(
            "At least one database table is required."
        )


    # ========================================================
    # GET SCHEMA
    # ========================================================

    schema = get_schema(
        user_email,
        tables
    )


    if not schema:

        raise ValueError(
            "No database schema available "
            "for the selected tables."
        )


    # ========================================================
    # GET DATASET NAME
    # ========================================================

    if len(tables) == 1:

        dataset_name = tables[0]

    else:

        dataset_name = ", ".join(
            tables
        )


    # ========================================================
    # LOAD CHAT MEMORY
    # ========================================================

    print(
        "Loading conversation memory..."
    )

    memory = get_conversation_memory(

        user_email=user_email,

        dataset_name=dataset_name,

        question=question
    )


    # ========================================================
    # SQL GENERATION PROMPT
    # ========================================================

    prompt = f"""
You are an expert PostgreSQL Business Analyst.

Your job is to convert the user's business question
into ONE correct PostgreSQL SELECT query.

============================================================
DATABASE SCHEMA
============================================================

{schema}

============================================================
CONVERSATION MEMORY
============================================================

{memory}

============================================================
CURRENT USER QUESTION
============================================================

{question}

============================================================
IMPORTANT INSTRUCTIONS
============================================================

1. Return ONLY SQL.

2. Do not explain the SQL.

3. Do not use markdown.

4. Return exactly ONE SELECT or WITH query.

5. Use ONLY tables and columns present in the database schema.

6. Never invent a table.

7. Never invent a column.

8. Use valid PostgreSQL syntax.

9. Preserve category names, product names,
   customer names and region names.

10. For aggregation questions use appropriate functions
    such as SUM, COUNT, AVG, MIN or MAX.

11. When grouping results, include the grouping column
    in SELECT and GROUP BY.

12. For "top" questions use:

    ORDER BY ... DESC
    LIMIT N

13. For "lowest" questions use:

    ORDER BY ... ASC
    LIMIT N

14. Do not add LIMIT unless the user asks for
    top, bottom or a specific number.

15. For monthly trends use:

    DATE_TRUNC('month', date_column)

16. For yearly trends use:

    DATE_TRUNC('year', date_column)

17. For daily trends use:

    DATE_TRUNC('day', date_column)

18. Always ORDER BY the date when producing
    a time series.

19. If the current question refers to something
    from the previous conversation, use the
    conversation memory to understand it.

20. Examples of follow-up questions include:

    "Which one is better?"

    "Why?"

    "What about the other one?"

    "Show me more."

    "Compare them."

    "Why is it higher?"

21. Do not ask the user to repeat information
    that already exists in the conversation memory.

22. Use the current database schema together
    with the conversation memory.

23. The final query must answer the CURRENT
    question.

24. Never generate INSERT, UPDATE, DELETE,
    DROP, ALTER or TRUNCATE.

============================================================
EXAMPLES
============================================================

Example 1:

Question:

What is our total revenue?

SQL:

SELECT
    SUM(revenue) AS total_revenue
FROM test_sales;


Example 2:

Question:

What is our revenue by category?

SQL:

SELECT
    category,
    SUM(revenue) AS total_revenue
FROM test_sales
GROUP BY category
ORDER BY total_revenue DESC;


Example 3:

Question:

What are our top 5 products by revenue?

SQL:

SELECT
    product,
    SUM(revenue) AS total_revenue
FROM test_sales
GROUP BY product
ORDER BY total_revenue DESC
LIMIT 5;


Example 4:

Question:

What is our revenue by month?

SQL:

SELECT
    DATE_TRUNC('month', date) AS month,
    SUM(revenue) AS total_revenue
FROM test_sales
GROUP BY DATE_TRUNC('month', date)
ORDER BY month;


============================================================
FINAL TASK
============================================================

Generate ONE PostgreSQL SELECT query
that answers the current user's question.

Return ONLY the SQL.
"""


    # ========================================================
    # CALL OLLAMA
    # ========================================================

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


    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    try:

        raw_response = response[
            "message"
        ][
            "content"
        ]

    except Exception as e:

        raise ValueError(
            f"Could not read Ollama response: {e}"
        )


    # ========================================================
    # CLEAN SQL
    # ========================================================

    sql = clean_sql(
        raw_response
    )


    # ========================================================
    # BASIC VALIDATION
    # ========================================================

    if not sql:

        raise ValueError(
            "AI returned an empty SQL query."
        )


    if not re.match(
        r"^(SELECT|WITH)\b",
        sql,
        flags=re.IGNORECASE
    ):

        raise ValueError(
            "AI did not generate a valid SELECT query."
        )


    # ========================================================
    # BLOCK DANGEROUS SQL
    # ========================================================

    sql_upper = sql.upper()

    forbidden_keywords = [

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


    for keyword in forbidden_keywords:

        if keyword in sql_upper:

            raise ValueError(
                "AI generated unsafe SQL."
            )


    # ========================================================
    # RETURN SQL
    # ========================================================

    return sql


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================================"
    )

    print(
        "AI BUSINESS ANALYST - SQL AGENT TEST"
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


    question = input(
        "Ask a business question: "
    ).strip()


    tables = [
        dataset
    ]


    print()

    print(
        "Loading conversation memory..."
    )


    print(
        "Generating SQL..."
    )


    try:

        sql = generate_sql(

            question=question,

            tables=tables,

            user_email=email
        )


        print()

        print(
            "Generated SQL:"
        )

        print()

        print(
            sql
        )


        print()

        print(
            "============================================================"
        )

        print(
            "✅ SQL AGENT TEST COMPLETED"
        )

        print(
            "============================================================"
        )


    except Exception as e:

        print()

        print(
            "❌ SQL generation failed:"
        )

        print(
            str(e)
        )