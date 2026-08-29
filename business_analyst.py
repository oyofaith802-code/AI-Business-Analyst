from question_router import classify_question
from document_agent import answer_document_question

from sql_agent import generate_sql
from database import run_query
from question_router import classify_question


from analysis_engine import analyze_business_question


# ============================================================
# GET AVAILABLE TABLES
# ============================================================

def get_available_tables():

    try:

        from schema import get_tables

        tables = get_tables()

        if tables:
            return tables

    except Exception:
        pass


    # Fallback: read PostgreSQL tables directly

    try:

        from database import engine
        from sqlalchemy import text

        with engine.connect() as connection:

            result = connection.execute(
                text("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name
                """)
            )

            return [
                row[0]
                for row in result.fetchall()
            ]

    except Exception:
        return []


# ============================================================
# SELECT TABLES
# ============================================================

def select_tables_for_question(question, tables):

    if not tables:
        return []

    try:

        from table_selector import select_tables

        return select_tables(
            question,
            tables
        )

    except Exception:
        pass


    # --------------------------------------------------------
    # Simple fallback
    # --------------------------------------------------------

    question_lower = question.lower()

    selected = []

    for table in tables:

        table_lower = table.lower()

        if (
            table_lower.rstrip("s")
            in question_lower
            or table_lower
            in question_lower
        ):
            selected.append(table)


    # Common Olist relationships

    if "product" in question_lower:

        if "order_items" in tables:
            selected.append("order_items")

        if "products" in tables:
            selected.append("products")


    if "sales" in question_lower:

        if "order_items" in tables:
            selected.append("order_items")

        if "payments" in tables:
            selected.append("payments")


    if "order" in question_lower:

        if "orders" in tables:
            selected.append("orders")


    # Remove duplicates

    return list(
        dict.fromkeys(selected)
    )


# ============================================================
# DATABASE QUESTION
# ============================================================

def answer_database_question(
    user_email,
    question
):

    try:

        result = analyze_business_question(
            question=question,
            user_email=user_email,
        )

    except Exception as e:

        return (
            f"Business analysis error: {e}"
        )


    if not result.get("success"):

        return result.get(
            "error",
            "Business analysis failed."
        )


    return result.get(
        "answer",
        "No answer was generated."
    )


# ============================================================
# BOTH DATABASE + DOCUMENT
# ============================================================

def answer_both(
    user_email,
    question
):

    database_answer = answer_database_question(
        user_email,
        question
    )


    document_answer = answer_document_question(
        user_email,
        question
    )


    return f"""
### Database Analysis

{database_answer}


### Document Analysis

{document_answer}
""".strip()


# ============================================================
# MAIN BUSINESS ANALYST
# ============================================================

def answer_business_question(
    user_email,
    question
):

    route = classify_question(
        question
    )


    # --------------------------------------------------------
    # DATABASE
    # --------------------------------------------------------

    if route == "DATABASE":

        answer = answer_database_question(
            user_email,
            question
        )

        return {
            "route": "DATABASE",
            "answer": answer
        }


    # --------------------------------------------------------
    # DOCUMENT
    # --------------------------------------------------------

    if route == "DOCUMENT":

        answer = answer_document_question(
            user_email,
            question
        )

        return {
            "route": "DOCUMENT",
            "answer": answer
        }


    # --------------------------------------------------------
    # BOTH
    # --------------------------------------------------------

    if route == "BOTH":

        answer = answer_both(
            user_email,
            question
        )

        return {
            "route": "BOTH",
            "answer": answer
        }


    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return {
        "route": "DOCUMENT",
        "answer": answer_document_question(
            user_email,
            question
        )
    }