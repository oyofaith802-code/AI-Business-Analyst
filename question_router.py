from ollama import chat


# ============================================================
# KEYWORDS
# ============================================================

DATABASE_KEYWORDS = {
    "order",
    "orders",
    "customer",
    "customers",
    "product",
    "products",
    "payment",
    "payments",
    "review",
    "reviews",
    "sales",
    "sale",
    "revenue",
    "profit",
    "profits",
    "price",
    "prices",
    "quantity",
    "items",
    "item",
    "total",
    "average",
    "count",
    "number",
    "highest",
    "lowest",
    "most",
    "least",
    "best",
    "worst",
    "top",
    "monthly",
    "weekly",
    "daily",
    "yearly",
    "trend",
}


DOCUMENT_KEYWORDS = {
    "report",
    "reports",
    "document",
    "documents",
    "recommendation",
    "recommendations",
    "management",
    "policy",
    "policies",
    "mentioned",
    "according",
    "written",
    "statement",
    "strategy",
    "strategies",
    "outlook",
    "memo",
}


COMPARISON_KEYWORDS = {
    "compare",
    "comparison",
    "against",
    "versus",
    "vs",
    "both",
}


# ============================================================
# GET WORDS
# ============================================================

def get_words(question):

    return set(
        question.lower()
        .replace("?", "")
        .replace(",", "")
        .replace(".", "")
        .replace("!", "")
        .split()
    )


# ============================================================
# CLASSIFY QUESTION
# ============================================================

def classify_question(question):

    words = get_words(
        question
    )

    database_matches = (
        words & DATABASE_KEYWORDS
    )

    document_matches = (
        words & DOCUMENT_KEYWORDS
    )

    comparison_matches = (
        words & COMPARISON_KEYWORDS
    )


    # ========================================================
    # RULE 1 — BOTH
    # ========================================================
    #
    # This MUST happen before DATABASE.
    #

    if (
        database_matches
        and document_matches
        and comparison_matches
    ):

        return "BOTH"


    # ========================================================
    # RULE 2 — EXPLICIT DOCUMENT QUESTION
    # ========================================================

    explicit_document_words = {
        "report",
        "reports",
        "document",
        "documents",
        "recommendation",
        "recommendations",
        "management",
        "policy",
        "policies",
        "outlook",
        "memo",
    }

    if words & explicit_document_words:

        # If there is no database comparison,
        # this is a document question.

        if not comparison_matches:

            return "DOCUMENT"


    # ========================================================
    # RULE 3 — STRONG DATABASE QUESTION
    # ========================================================

    strong_database_words = {
        "order",
        "orders",
        "customer",
        "customers",
        "product",
        "products",
        "payment",
        "payments",
        "review",
        "reviews",
        "sales",
        "sale",
        "quantity",
        "items",
        "item",
        "profit",
        "profits",
    }

    if words & strong_database_words:

        return "DATABASE"


    # ========================================================
    # RULE 4 — DATABASE SIGNAL
    # ========================================================

    if database_matches:

        return "DATABASE"


    # ========================================================
    # RULE 5 — DOCUMENT SIGNAL
    # ========================================================

    if document_matches:

        return "DOCUMENT"


    # ========================================================
    # RULE 6 — OLLAMA FALLBACK
    # ========================================================

    prompt = f"""
You are the routing system for an AI Business Analyst.

Classify the question into exactly one category:

DATABASE
DOCUMENT
BOTH

DATABASE:
Questions requiring structured business database data,
including orders, customers, products, payments, reviews,
sales, totals, counts, rankings, calculations and trends.

DOCUMENT:
Questions asking about uploaded PDF/DOCX files,
business reports, management reports, recommendations,
policies or other written information.

BOTH:
Questions that explicitly require information from BOTH
the business database and uploaded documents.

Examples:

"How many orders did we receive?"
DATABASE

"Which product generated the most sales?"
DATABASE

"What revenue is mentioned in the report?"
DOCUMENT

"What recommendation did management make?"
DOCUMENT

"Compare our sales with the recommendation in the report."
BOTH

Return only one word.

Question:
{question}

Answer:
"""


    try:

        response = chat(
            model="llama3.2",
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        result = (
            response["message"]["content"]
            .strip()
            .upper()
        )

    except Exception:

        return "DOCUMENT"


    if result == "DATABASE":
        return "DATABASE"

    if result == "DOCUMENT":
        return "DOCUMENT"

    if result == "BOTH":
        return "BOTH"


    return "DOCUMENT"