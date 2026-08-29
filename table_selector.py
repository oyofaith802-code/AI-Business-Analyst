from database import engine
from sqlalchemy import inspect, text
from schema_memory import clean_email


# ============================================================
# BUILT-IN SYSTEM / BUSINESS TABLES
# ============================================================

BUILTIN_TABLES = {
    "products",
    "order_items",
    "orders",
    "payments",
    "customers",
    "reviews",
}


# ============================================================
# SYSTEM TABLES - NEVER SELECT AS USER DATA
# ============================================================

SYSTEM_TABLES = {
    "users",
    "workspace",
    "workspaces",
    "schema_memory",
    "dataset_memory",
    "dataset_profiles",
    "business_memory",
    "relationship_memory",
    "document_memory",
    "chat_memory",
    "chat_history",
    "projects",
    "subscriptions",
    "usage_tracking",
}


# ============================================================
# GET ALL DATABASE TABLES
# ============================================================

def get_all_tables():

    inspector = inspect(engine)

    tables = inspector.get_table_names()

    return [
        table
        for table in tables
        if table not in SYSTEM_TABLES
    ]


# ============================================================
# GET USER OWNED DATASETS
# ============================================================

def get_uploaded_datasets(user_email):

    user_email = clean_email(user_email)

    if not user_email:
        return []

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text("""
                    SELECT DISTINCT dataset_name
                    FROM dataset_profiles
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
                if row[0]
            ]

    except Exception as e:

        print(
            f"Could not load user datasets: {e}"
        )

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

    import re

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

    if not user_email:

        print(
            "ERROR: User email is required."
        )

        return []

    print(
        "Finding available tables..."
    )

    all_tables = get_all_tables()

    # --------------------------------------------------------
    # GET USER-OWNED DATASETS
    # --------------------------------------------------------

    uploaded = get_uploaded_datasets(
        user_email
    )

    uploaded_set = set(
        uploaded
    )

    # --------------------------------------------------------
    # IMPORTANT SECURITY BOUNDARY
    #
    # A physical table is considered selectable if:
    #
    # 1. It is a built-in business table, OR
    # 2. It belongs to this user.
    #
    # Every other table is ignored.
    # --------------------------------------------------------

    selectable_tables = []

    for table in all_tables:

        if table in BUILTIN_TABLES:

            selectable_tables.append(
                table
            )

        elif table in uploaded_set:

            selectable_tables.append(
                table
            )

    print(
        "Available tables for this user:"
    )

    for table in selectable_tables:

        print(
            f"• {table}"
        )

    print(
        "\nUploaded datasets owned by this user:"
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
    # SCORE ONLY SAFE TABLES
    # --------------------------------------------------------

    scored_tables = []

    for table in selectable_tables:

        columns = get_table_columns(
            table
        )

        score = score_table(
            question,
            table,
            columns
        )

        # Give owned datasets priority.
        if table in uploaded_set:

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
    # STRONG USER DATASET MATCH
    # --------------------------------------------------------

    uploaded_matches = []

    for table, score in scored_tables:

        if (
            table in uploaded_set
            and score > 0
        ):

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
        "\nSelected tables:"
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
