import re

from database import engine
from sqlalchemy import inspect, text

from schema_memory import clean_email


# ============================================================
# GET ALL DATABASE TABLES
# ============================================================

def get_all_tables():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    excluded = {
        "users",
        "workspace",
        "schema_memory",
        "dataset_memory"
    }

    return [
        table
        for table in tables
        if table not in excluded
    ]


# ============================================================
# GET USER UPLOADED DATASETS
# ============================================================

def get_uploaded_datasets(user_email):

    user_email = clean_email(user_email)

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT DISTINCT dataset_name
                    FROM dataset_memory
                    WHERE user_email = :user_email
                    ORDER BY dataset_name
                """),
                {
                    "user_email": user_email
                }
            )

            rows = result.fetchall()

            return [
                row[0]
                for row in rows
            ]

    except Exception:

        return []


# ============================================================
# GET TABLE SCHEMA
# ============================================================

def get_table_columns(table_name):

    inspector = inspect(engine)

    try:

        columns = inspector.get_columns(
            table_name
        )

        return [
            column["name"]
            for column in columns
        ]

    except Exception:

        return []


# ============================================================
# NORMALIZE TEXT
# ============================================================

def normalize_text(text_value):

    text_value = str(
        text_value
    ).lower()

    text_value = re.sub(
        r"[^a-z0-9_ ]",
        " ",
        text_value
    )

    text_value = re.sub(
        r"\s+",
        " ",
        text_value
    )

    return text_value.strip()


# ============================================================
# SCORE TABLE
# ============================================================

def score_table(
    question,
    table_name,
    columns
):

    question_text = normalize_text(
        question
    )

    table_text = normalize_text(
        table_name
    )

    score = 0

    # --------------------------------------------------------
    # TABLE NAME MATCH
    # --------------------------------------------------------

    table_words = table_text.replace(
        "_",
        " "
    ).split()

    for word in table_words:

        if len(word) >= 3 and word in question_text:

            score += 5

    # --------------------------------------------------------
    # COLUMN MATCH
    # --------------------------------------------------------

    for column in columns:

        column_text = normalize_text(
            column
        )

        column_words = column_text.replace(
            "_",
            " "
        ).split()

        for word in column_words:

            if len(word) >= 3 and word in question_text:

                score += 3

    # --------------------------------------------------------
    # BUSINESS KEYWORDS
    # --------------------------------------------------------

    business_keywords = {
        "sales": [
            "revenue",
            "sales",
            "amount",
            "price",
            "total"
        ],

        "revenue": [
            "revenue",
            "sales",
            "income",
            "amount"
        ],

        "product": [
            "product",
            "products",
            "item",
            "items"
        ],

        "customer": [
            "customer",
            "customers",
            "buyer",
            "buyers"
        ],

        "order": [
            "order",
            "orders"
        ],

        "quantity": [
            "quantity",
            "units",
            "sold"
        ],

        "category": [
            "category",
            "categories"
        ]
    }

    for category, keywords in business_keywords.items():

        category_match = any(
            keyword in question_text
            for keyword in keywords
        )

        if not category_match:

            continue

        for column in columns:

            column_text = normalize_text(
                column
            )

            if any(
                keyword in column_text
                for keyword in keywords
            ):

                score += 8

    return score


# ============================================================
# SELECT RELEVANT TABLES
# ============================================================

def select_relevant_tables(
    question,
    user_email
):

    user_email = clean_email(
        user_email
    )

    print(
        "🔍 Finding available tables..."
    )

    all_tables = get_all_tables()

    print(
        "📋 Available tables:"
    )

    for table in all_tables:

        print(
            f"• {table}"
        )

    # --------------------------------------------------------
    # USER UPLOADED DATASETS
    # --------------------------------------------------------

    uploaded = get_uploaded_datasets(
        user_email
    )

    print(
        "\n📂 Uploaded datasets:"
    )

    if uploaded:

        for table in uploaded:

            print(
                f"• {table}"
            )

    else:

        print(
            "• None"
        )

    # --------------------------------------------------------
    # SCORE TABLES
    # --------------------------------------------------------

    print(
        "\n🧠 Selecting relevant tables..."
    )

    scored_tables = []

    for table in all_tables:

        columns = get_table_columns(
            table
        )

        score = score_table(
            question,
            table,
            columns
        )

        # Uploaded datasets get priority
        if table in uploaded:

            score += 20

        scored_tables.append(
            (
                table,
                score
            )
        )

    scored_tables.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # --------------------------------------------------------
    # SELECT TABLES
    # --------------------------------------------------------

    selected = []

    if scored_tables:

        best_score = scored_tables[0][1]

        for table, score in scored_tables:

            if score <= 0:

                continue

            # Keep tables close to the best match
            if score >= max(
                1,
                best_score - 5
            ):

                selected.append(
                    table
                )

            if len(selected) >= 5:

                break

    # --------------------------------------------------------
    # IF AN UPLOADED DATASET EXISTS,
    # PREFER IT WHEN IT HAS A STRONG MATCH
    # --------------------------------------------------------

    uploaded_matches = []

    for table, score in scored_tables:

        if table in uploaded and score > 0:

            uploaded_matches.append(
                (
                    table,
                    score
                )
            )

    if uploaded_matches:

        uploaded_matches.sort(
            key=lambda item: item[1],
            reverse=True
        )

        best_uploaded = uploaded_matches[0]

        # If uploaded dataset has a meaningful match,
        # use it instead of unrelated legacy tables.

        if best_uploaded[1] >= 8:

            selected = [
                best_uploaded[0]
            ]

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    selected = list(
        dict.fromkeys(
            selected
        )
    )

    print(
        "✅ Selected tables:"
    )

    for table in selected:

        print(
            f"• {table}"
        )

    return selected


# ============================================================
# COMMAND LINE TEST
# ============================================================

def main():

    email = input(
        "Enter user email: "
    ).strip()

    question = input(
        "Ask a business question: "
    ).strip()

    selected = select_relevant_tables(
        question,
        email
    )

    print(
        "\nFINAL TABLE SELECTION:"
    )

    for table in selected:

        print(
            f"• {table}"
        )


if __name__ == "__main__":

    main()