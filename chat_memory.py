# ============================================================
# AI BUSINESS ANALYST
# CHAT MEMORY
# ============================================================

from sqlalchemy import text

from database import engine


# ============================================================
# CREATE / REPAIR CHAT MEMORY TABLE
# ============================================================

def create_chat_memory_table():

    with engine.begin() as conn:

        # ----------------------------------------------------
        # Create table if it does not exist
        # ----------------------------------------------------

        conn.execute(
            text(
                """
                CREATE TABLE IF NOT EXISTS chat_memory (

                    id SERIAL PRIMARY KEY,

                    user_email TEXT,

                    dataset_name TEXT,

                    question TEXT,

                    answer TEXT,

                    sql_query TEXT,

                    created_at TIMESTAMP
                    DEFAULT CURRENT_TIMESTAMP

                )
                """
            )
        )

        # ----------------------------------------------------
        # Repair missing columns
        # ----------------------------------------------------

        columns = conn.execute(
            text(
                """
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = 'chat_memory'
                """
            )
        ).fetchall()

        existing_columns = {
            row[0]
            for row in columns
        }

        required_columns = {

            "user_email":
                "TEXT",

            "dataset_name":
                "TEXT",

            "question":
                "TEXT",

            "answer":
                "TEXT",

            "sql_query":
                "TEXT",

            "created_at":
                "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
        }

        for column, data_type in required_columns.items():

            if column not in existing_columns:

                conn.execute(
                    text(
                        f"""
                        ALTER TABLE chat_memory
                        ADD COLUMN {column}
                        {data_type}
                        """
                    )
                )

                print(
                    f"✅ Added missing column: {column}"
                )

    print(
        "✅ chat_memory table ready."
    )


# ============================================================
# SAVE CHAT
# ============================================================

def save_chat(
    user_email,
    dataset_name,
    question,
    answer,
    sql_query=None
):

    if not user_email:

        return False

    if not question:

        return False

    create_chat_memory_table()

    sql = text(
        """
        INSERT INTO chat_memory (

            user_email,
            dataset_name,
            question,
            answer,
            sql_query

        )

        VALUES (

            :user_email,
            :dataset_name,
            :question,
            :answer,
            :sql_query

        )
        """
    )

    try:

        with engine.begin() as conn:

            conn.execute(
                sql,
                {
                    "user_email":
                        user_email,

                    "dataset_name":
                        dataset_name,

                    "question":
                        question,

                    "answer":
                        answer,

                    "sql_query":
                        sql_query
                }
            )

        print(
            "✅ Chat saved."
        )

        return True

    except Exception as e:

        print(
            f"❌ Could not save chat: {e}"
        )

        return False


# ============================================================
# GET CHAT HISTORY
# ============================================================

def get_chat_history(
    user_email,
    dataset_name=None,
    limit=10
):

    if not user_email:

        return []

    create_chat_memory_table()

    try:

        if dataset_name:

            sql = text(
                """
                SELECT

                    id,
                    user_email,
                    dataset_name,
                    question,
                    answer,
                    sql_query,
                    created_at

                FROM chat_memory

                WHERE user_email = :user_email

                AND dataset_name = :dataset_name

                ORDER BY created_at DESC

                LIMIT :limit
                """
            )

            params = {

                "user_email":
                    user_email,

                "dataset_name":
                    dataset_name,

                "limit":
                    limit
            }

        else:

            sql = text(
                """
                SELECT

                    id,
                    user_email,
                    dataset_name,
                    question,
                    answer,
                    sql_query,
                    created_at

                FROM chat_memory

                WHERE user_email = :user_email

                ORDER BY created_at DESC

                LIMIT :limit
                """
            )

            params = {

                "user_email":
                    user_email,

                "limit":
                    limit
            }


        with engine.connect() as conn:

            result = conn.execute(
                sql,
                params
            )

            rows = result.mappings().all()


        return [
            dict(row)
            for row in rows
        ]


    except Exception as e:

        print(
            f"❌ Could not load chat history: {e}"
        )

        return []


# ============================================================
# GET LAST CHAT
# ============================================================

def get_last_chat(
    user_email,
    dataset_name=None
):

    history = get_chat_history(
        user_email,
        dataset_name,
        limit=1
    )

    if not history:

        return None

    return history[0]


# ============================================================
# GET ALL USER HISTORY
# ============================================================

def get_all_chat_history(
    user_email
):

    if not user_email:

        return []

    create_chat_memory_table()

    sql = text(
        """
        SELECT

            id,
            dataset_name,
            question,
            answer,
            sql_query,
            created_at

        FROM chat_memory

        WHERE user_email = :user_email

        ORDER BY created_at DESC
        """
    )

    try:

        with engine.connect() as conn:

            result = conn.execute(
                sql,
                {
                    "user_email":
                        user_email
                }
            )

            rows = result.mappings().all()


        return [
            dict(row)
            for row in rows
        ]


    except Exception as e:

        print(
            f"❌ Could not load history: {e}"
        )

        return []


# ============================================================
# DELETE DATASET HISTORY
# ============================================================

def delete_dataset_chat_history(
    user_email,
    dataset_name
):

    if not user_email:

        return False

    sql = text(
        """
        DELETE FROM chat_memory

        WHERE user_email = :user_email

        AND dataset_name = :dataset_name
        """
    )

    try:

        with engine.begin() as conn:

            result = conn.execute(
                sql,
                {
                    "user_email":
                        user_email,

                    "dataset_name":
                        dataset_name
                }
            )

        print(
            f"✅ Deleted {result.rowcount} chat records."
        )

        return True


    except Exception as e:

        print(
            f"❌ Could not delete chat history: {e}"
        )

        return False


# ============================================================
# DELETE ALL USER HISTORY
# ============================================================

def delete_all_chat_history(
    user_email
):

    if not user_email:

        return False

    sql = text(
        """
        DELETE FROM chat_memory

        WHERE user_email = :user_email
        """
    )

    try:

        with engine.begin() as conn:

            result = conn.execute(
                sql,
                {
                    "user_email":
                        user_email
                }
            )

        print(
            f"✅ Deleted {result.rowcount} chat records."
        )

        return True


    except Exception as e:

        print(
            f"❌ Could not delete chat history: {e}"
        )

        return False


# ============================================================
# FORMAT HISTORY
# ============================================================

def format_chat_history(
    history,
    max_items=10
):

    if not history:

        return "No previous conversation."


    recent_history = history[
        :max_items
    ]


    parts = []


    for item in reversed(
        recent_history
    ):

        question = item.get(
            "question",
            ""
        )

        answer = item.get(
            "answer",
            ""
        )


        parts.append(
            f"""
Previous user question:
{question}

Previous AI answer:
{answer}
"""
        )


    return "\n".join(
        parts
    )


# ============================================================
# BUILD MEMORY CONTEXT
# ============================================================

def build_memory_context(
    user_email,
    dataset_name,
    current_question,
    limit=10
):

    history = get_chat_history(
        user_email,
        dataset_name,
        limit
    )


    history_text = format_chat_history(
        history,
        limit
    )


    return f"""
You are an AI Business Analyst.

Current dataset:
{dataset_name}

Previous conversation:

{history_text}

Current user question:
{current_question}

Use previous conversation when relevant.

If the user says:

- "that category"
- "which one"
- "the previous result"
- "compare them"
- "what about the other one"
- "show me more"
- "why is it higher"

use the previous conversation to understand
what they mean.

Do not invent information.
Use only information available in the
conversation and database.
"""


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================================"
    )

    print(
        "CHAT MEMORY TEST"
    )

    print(
        "============================================================"
    )

    # --------------------------------------------------------
    # Create / repair table
    # --------------------------------------------------------

    create_chat_memory_table()


    # --------------------------------------------------------
    # Test data
    # --------------------------------------------------------

    test_email = "test@example.com"

    test_dataset = "test_sales"


    # --------------------------------------------------------
    # Save test conversation
    # --------------------------------------------------------

    save_chat(

        user_email=test_email,

        dataset_name=test_dataset,

        question=(
            "What is our revenue by category?"
        ),

        answer=(
            "Electronics: 270000. "
            "Furniture: 115000."
        ),

        sql_query="""
SELECT
    category,
    SUM(revenue) AS total_revenue
FROM test_sales
GROUP BY category;
"""
    )


    # --------------------------------------------------------
    # Load history
    # --------------------------------------------------------

    history = get_chat_history(

        test_email,

        test_dataset,

        limit=10
    )


    print(
        f"Found {len(history)} chat records."
    )


    # --------------------------------------------------------
    # Display history
    # --------------------------------------------------------

    print(
        format_chat_history(
            history
        )
    )


    # --------------------------------------------------------
    # Memory context
    # --------------------------------------------------------

    context = build_memory_context(

        test_email,

        test_dataset,

        "Which category is performing better?"
    )


    print(
        "============================================================"
    )

    print(
        "MEMORY CONTEXT"
    )

    print(
        "============================================================"
    )

    print(
        context
    )


    print(
        "============================================================"
    )

    print(
        "✅ CHAT MEMORY TEST COMPLETED"
    )

    print(
        "============================================================"
    )