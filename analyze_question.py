import re
from llm import ask_ai
from schema_memory import get_schema


# ============================================================
# AI BUSINESS ANALYST - QUESTION ANALYZER
# ============================================================

def analyze_question(question, user_email="solomonenamudu@gmail.com"):

    print("\n🔍 Reading database schema...")

    schema = get_schema(user_email)

    if not schema:
        return {
            "answerable": False,
            "reason": "No database schema was found.",
            "tables": [],
            "columns": []
        }

    prompt = f"""
You are a database reasoning agent for an AI Business Analyst.

Your job is to determine whether a business question can be answered
using the available database schema.

DATABASE SCHEMA:
{schema}

BUSINESS QUESTION:
{question}

IMPORTANT RULES:

1. Identify EVERY table required to answer the question.
2. Identify EVERY important column required.
3. Think about relationships between tables.
4. Do not select tables merely because they exist.
5. If product category is requested, products.product_category_name
   is required.
6. If product sales/revenue is requested, order_items.price is required.
7. If customer information is requested, customers may be required.
8. If payment information is requested, payments may be required.
9. If the question requires multiple tables, include ALL of them.
10. Do not invent tables or columns.
11. A question is ANSWERABLE if the required information exists
    in the schema and the tables can logically be joined.

COMMON RELATIONSHIPS:

products.product_id = order_items.product_id

orders.order_id = order_items.order_id

orders.order_id = payments.order_id

orders.customer_id = customers.customer_id

orders.order_id = reviews.order_id

Return EXACTLY this format:

ANSWERABLE: YES or NO
REASON: <short explanation>
TABLES: table1, table2, table3
COLUMNS: table.column, table.column, table.column

BUSINESS QUESTION:
{question}
"""

    print("\n🧠 Checking whether the question can be answered...")

    try:

        response = ask_ai(prompt)

        if isinstance(response, dict):

            raw_response = response.get("content", "")

        else:

            raw_response = str(response)

    except Exception as e:

        return {
            "answerable": False,
            "reason": f"AI analysis failed: {e}",
            "tables": [],
            "columns": []
        }


    # ========================================================
    # PARSE ANSWERABLE
    # ========================================================

    answerable_match = re.search(
        r"ANSWERABLE\s*:\s*(YES|NO)",
        raw_response,
        re.IGNORECASE
    )

    answerable = False

    if answerable_match:

        answerable = (
            answerable_match.group(1).upper() == "YES"
        )


    # ========================================================
    # PARSE REASON
    # ========================================================

    reason_match = re.search(
        r"REASON\s*:\s*(.*?)(?=\nTABLES\s*:|\nCOLUMNS\s*:|$)",
        raw_response,
        re.IGNORECASE | re.DOTALL
    )

    reason = ""

    if reason_match:

        reason = reason_match.group(1).strip()


    # ========================================================
    # PARSE TABLES
    # ========================================================

    tables_match = re.search(
        r"TABLES\s*:\s*(.*?)(?=\nCOLUMNS\s*:|$)",
        raw_response,
        re.IGNORECASE | re.DOTALL
    )

    tables = []

    if tables_match:

        table_text = tables_match.group(1).strip()

        tables = [
            table.strip()
            for table in table_text.split(",")
            if table.strip()
        ]


    # ========================================================
    # PARSE COLUMNS
    # ========================================================

    columns_match = re.search(
        r"COLUMNS\s*:\s*(.*)$",
        raw_response,
        re.IGNORECASE | re.DOTALL
    )

    columns = []

    if columns_match:

        column_text = columns_match.group(1).strip()

        columns = [
            column.strip()
            for column in column_text.split(",")
            if column.strip()
        ]


    # ========================================================
    # RETURN STRUCTURED RESULT
    # ========================================================

    return {
        "answerable": answerable,
        "reason": reason,
        "tables": tables,
        "columns": columns,
        "raw_response": raw_response
    }


# ============================================================
# TEST MODE
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("🤖 AI BUSINESS ANALYST - QUESTION ANALYZER")
    print("=" * 60)

    question = input(
        "\nAsk a business question: "
    ).strip()

    result = analyze_question(question)

    print("\n" + "=" * 60)

    if result["answerable"]:

        print("✅ ANSWERABLE")

    else:

        print("❌ NOT ANSWERABLE")


    print("\nReason:")
    print(result["reason"])


    print("\nRelevant tables:")

    for table in result["tables"]:

        print(f"• {table}")


    print("\nRelevant columns:")

    for column in result["columns"]:

        print(f"• {column}")


    print("\n" + "=" * 60)