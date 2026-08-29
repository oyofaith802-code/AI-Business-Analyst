import re
import ollama

from schema_memory import get_schema
from analyze_question import analyze_question


# ============================================================
# CLEAN SQL
# ============================================================

def clean_sql(sql):

    sql = sql.strip()

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

    sql = re.sub(
        r"^(SQL QUERY|GENERATED SQL|SQL)\s*:\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    return sql.strip()


# ============================================================
# EXTRACT TABLES
# ============================================================

def extract_tables(sql):

    tables = set()

    pattern = r"""
        \bFROM\s+([a-zA-Z_][a-zA-Z0-9_]*)
        |
        \bJOIN\s+([a-zA-Z_][a-zA-Z0-9_]*)
    """

    matches = re.findall(
        pattern,
        sql,
        flags=re.IGNORECASE | re.VERBOSE
    )

    for match in matches:

        for table in match:

            if table:
                tables.add(
                    table.lower()
                )

    return tables


# ============================================================
# EXTRACT ALIASES
# ============================================================

def extract_aliases(sql):

    aliases = set()

    pattern = r"""
        \bFROM\s+[a-zA-Z_][a-zA-Z0-9_]*
        \s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)

        |

        \bJOIN\s+[a-zA-Z_][a-zA-Z0-9_]*
        \s+(?:AS\s+)?([a-zA-Z_][a-zA-Z0-9_]*)
    """

    matches = re.findall(
        pattern,
        sql,
        flags=re.IGNORECASE | re.VERBOSE
    )

    for match in matches:

        for alias in match:

            if alias:
                aliases.add(
                    alias.lower()
                )

    return aliases


# ============================================================
# VALIDATE REQUIRED TABLES
# ============================================================

def validate_required_tables(
    sql,
    required_tables
):

    sql_tables = extract_tables(sql)

    missing = []

    for table in required_tables:

        if table.lower() not in sql_tables:

            missing.append(table)

    return missing


# ============================================================
# VALIDATE TABLE REFERENCES
# ============================================================

def validate_table_references(sql):

    aliases = extract_aliases(sql)

    # Also allow actual table names
    tables = extract_tables(sql)

    allowed = aliases.union(tables)

    references = re.findall(
        r"\b([a-zA-Z_][a-zA-Z0-9_]*)\.",
        sql
    )

    unknown = set()

    for ref in references:

        ref = ref.lower()

        if ref not in allowed:

            unknown.add(ref)

    return sorted(unknown)


# ============================================================
# SPECIAL REPAIR FOR PRODUCT CATEGORY QUESTIONS
# ============================================================

def repair_product_category_sales_sql(
    question,
    sql
):

    question_lower = question.lower()

    category_words = [
        "product category",
        "product categories",
        "category",
        "categories"
    ]

    sales_words = [
        "sales",
        "revenue",
        "top",
        "highest",
        "most"
    ]

    is_category_question = any(
        word in question_lower
        for word in category_words
    )

    is_sales_question = any(
        word in question_lower
        for word in sales_words
    )

    if not (
        is_category_question
        and is_sales_question
    ):

        return sql

    # Determine LIMIT
    limit_match = re.search(
        r"\bLIMIT\s+(\d+)",
        sql,
        flags=re.IGNORECASE
    )

    limit = (
        limit_match.group(1)
        if limit_match
        else "1"
    )

    # If user asks top 5, make sure LIMIT is 5
    top_match = re.search(
        r"\btop\s+(\d+)",
        question_lower
    )

    if top_match:

        limit = top_match.group(1)

    # Build deterministic SQL
    # This avoids hallucinated joins.
    return f"""
SELECT
    p.product_category_name,
    SUM(oi.price) AS total_sales
FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id
GROUP BY p.product_category_name
ORDER BY total_sales DESC
LIMIT {limit};
""".strip()


# ============================================================
# GENERATE SQL
# ============================================================

def generate_sql(
    question,
    user_id=None
):

    print("\n🔍 Reading database schema...")

    schema = get_schema(user_id)

    print("\n🧠 Analyzing required tables...")

    analysis = analyze_question(question)

    if not analysis.get(
        "answerable",
        False
    ):

        raise Exception(
            analysis.get(
                "reason",
                "Question cannot be answered."
            )
        )

    required_tables = analysis.get(
        "tables",
        []
    )

    required_columns = analysis.get(
        "columns",
        []
    )

    # ========================================================
    # SPECIAL CASES
    # ========================================================

    repaired_special_sql = (
        repair_product_category_sales_sql(
            question,
            ""
        )
    )

    if repaired_special_sql:

        # Only use special SQL when it really
        # matches the category/sales question.
        question_lower = question.lower()

        if (
            ("category" in question_lower
             or "categories" in question_lower)
            and
            (
                "sales" in question_lower
                or "revenue" in question_lower
                or "top" in question_lower
                or "most" in question_lower
                or "highest" in question_lower
            )
        ):

            return repaired_special_sql

    # ========================================================
    # AI SQL GENERATION
    # ========================================================

    prompt = f"""
You are an expert PostgreSQL Business Analyst.

DATABASE SCHEMA:

{schema}

BUSINESS QUESTION:

{question}

REQUIRED TABLES:

{", ".join(required_tables)}

REQUIRED COLUMNS:

{", ".join(required_columns)}

Generate ONE PostgreSQL query.

STRICT RULES:

1. Use only tables and columns in the schema.

2. Every table referenced in SELECT, WHERE, JOIN,
   GROUP BY, HAVING or ORDER BY must actually appear
   in FROM or JOIN.

3. Never reference an alias before its table is joined.

4. Every JOIN must connect tables that have already
   been introduced.

5. If using:
   order_items.product_id
   then order_items MUST appear in FROM or JOIN.

6. For product category analysis, use:

   products.product_category_name

7. Product and order_items are related through:

   products.product_id = order_items.product_id

8. For sales calculations use:

   order_items.price

9. For top N questions use:

   ORDER BY metric DESC
   LIMIT N

10. Return ONLY SQL.

NO MARKDOWN.
NO EXPLANATION.
"""

    response = ollama.chat(
        model="llama3.2",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    sql = clean_sql(
        response["message"]["content"]
    )

    # ========================================================
    # CHECK TABLES
    # ========================================================

    missing_tables = validate_required_tables(
        sql,
        required_tables
    )

    unknown_aliases = validate_table_references(
        sql
    )

    # ========================================================
    # AUTOMATIC REPAIR
    # ========================================================

    if (
        missing_tables
        or unknown_aliases
    ):

        print(
            "\n🔧 SQL structure problem detected."
        )

        repair_prompt = f"""
Fix this PostgreSQL query.

BUSINESS QUESTION:
{question}

DATABASE SCHEMA:
{schema}

REQUIRED TABLES:
{", ".join(required_tables)}

CURRENT SQL:
{sql}

Problems:

Missing tables:
{", ".join(missing_tables)}

Unknown aliases:
{", ".join(unknown_aliases)}

IMPORTANT:

Every table referenced by a column must be
introduced using FROM or JOIN.

For example, this is INVALID:

FROM products p
JOIN orders o
    ON order_items.product_id = p.product_id

because order_items was never introduced.

This is VALID:

FROM products p
JOIN order_items oi
    ON p.product_id = oi.product_id

Return ONLY the corrected SQL.
No markdown.
No explanation.
"""

        repair_response = ollama.chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": repair_prompt
                }
            ]
        )

        sql = clean_sql(
            repair_response["message"]["content"]
        )

    # ========================================================
    # FINAL VALIDATION
    # ========================================================

    missing_tables = validate_required_tables(
        sql,
        required_tables
    )

    unknown_aliases = validate_table_references(
        sql
    )

    if missing_tables:

        raise Exception(
            "SQL is missing required tables: "
            + ", ".join(missing_tables)
        )

    if unknown_aliases:

        raise Exception(
            "SQL contains unknown table aliases: "
            + ", ".join(unknown_aliases)
        )

    return sql


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n" + "=" * 60
    )

    print(
        "🤖 AI BUSINESS ANALYST - SQL GENERATOR"
    )

    print(
        "=" * 60
    )

    question = input(
        "\nAsk a business question: "
    ).strip()

    try:

        sql = generate_sql(
            question
        )

        print(
            "\n" + "=" * 60
        )

        print(
            "GENERATED SQL"
        )

        print(
            "=" * 60
        )

        print(sql)

    except Exception as e:

        print(
            "\n❌ SQL GENERATION ERROR"
        )

        print(e)