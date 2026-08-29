# ============================================================
# AI BUSINESS ANALYST
# WITH CHAT MEMORY
# ============================================================

import pandas as pd

from database import engine
from sqlalchemy import text

from table_selector import select_relevant_tables
from dataset_reasoning import analyze_question
from sql_agent import generate_sql
from sql_validator import validate_sql
from chart_generator import create_chart

from chat_memory import (
    save_chat,
    get_chat_history,
    build_memory_context
)


# ============================================================
# EXECUTE SQL
# ============================================================

def execute_sql(sql):

    try:

        with engine.connect() as conn:

            result = conn.execute(
                text(sql)
            )

            rows = result.fetchall()
            columns = result.keys()

            return pd.DataFrame(
                rows,
                columns=columns
            )

    except Exception as e:

        print(
            f"❌ SQL execution failed: {e}"
        )

        return None


# ============================================================
# GET AVAILABLE TABLES
# ============================================================

def get_available_tables():

    try:

        query = text(
            """
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name
            """
        )

        with engine.connect() as conn:

            result = conn.execute(query)

            return [
                row[0]
                for row in result.fetchall()
            ]

    except Exception as e:

        print(
            f"❌ Could not get tables: {e}"
        )

        return []


# ============================================================
# DISPLAY TABLES
# ============================================================

def display_tables(tables):

    print("\n📋 Available tables:")

    for table in tables:

        print(
            f"• {table}"
        )


# ============================================================
# GENERATE BUSINESS ANSWER
# ============================================================

def generate_business_answer(
    question,
    result,
    memory_context=""
):

    try:

        from ollama import chat

        result_text = result.to_string(
            index=False
        )

        prompt = f"""
You are a professional AI Business Analyst.

You are analyzing a business dataset.

Previous conversation:

{memory_context}

Current question:

{question}

Current database result:

{result_text}

Rules:

1. Answer using ONLY the database result.
2. Use previous conversation when the
   current question refers to something
   previously discussed.
3. Do not invent numbers.
4. Do not invent facts.
5. Preserve category names.
6. Preserve product names.
7. Give a direct answer.
8. Give one useful business insight.
9. Keep the answer concise.
10. If the question is a follow-up question,
    use the previous conversation to understand
    what the user means.

Format:

Answer:

[direct answer]

Business insight:

[one useful insight]
"""

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

        return response[
            "message"
        ][
            "content"
        ]

    except Exception as e:

        print(
            f"⚠️ AI explanation failed: {e}"
        )

        return result.to_string(
            index=False
        )


# ============================================================
# ANALYZE QUESTION
# ============================================================

def analyze_business_question(
    question,
    user_email,
    dataset_name
):

    print("\n" + "=" * 60)

    print(
        "🧠 AI BUSINESS ANALYST"
    )

    print("=" * 60)

    print(
        f"\n📂 Dataset: {dataset_name}"
    )

    print(
        f"❓ Question: {question}"
    )

    # ========================================================
    # LOAD CHAT MEMORY
    # ========================================================

    print(
        "\n🧠 Loading conversation memory..."
    )

    try:

        history = get_chat_history(
            user_email=user_email,
            dataset_name=dataset_name,
            limit=10
        )

        memory_context = build_memory_context(
            user_email=user_email,
            dataset_name=dataset_name,
            current_question=question
        )

        if history:

            print(
                f"✅ Found {len(history)} previous conversations."
            )

        else:

            print(
                "ℹ️ No previous conversation found."
            )

    except Exception as e:

        print(
            f"⚠️ Memory loading failed: {e}"
        )

        history = []

        memory_context = ""

    # ========================================================
    # FIND RELEVANT TABLES
    # ========================================================

    print(
        "\n🔍 Finding relevant tables..."
    )

    try:

        selected_tables = select_relevant_tables(

            question,

            user_email

        )

    except Exception as e:

        print(
            f"❌ Table selection failed: {e}"
        )

        return None

    if not selected_tables:

        print(
            "❌ No relevant tables found."
        )

        return None

    print(
        "\n✅ Selected tables:"
    )

    for table in selected_tables:

        print(
            f"• {table}"
        )

    # ========================================================
    # QUESTION REASONING
    # ========================================================

    print(
        "\n🧠 Checking whether the question can be answered..."
    )

    try:

        analysis = analyze_question(

            question,

            selected_tables,

            user_email

        )

    except Exception as e:

        print(
            f"❌ Question analysis failed: {e}"
        )

        return None

    print(
        "\n🧠 Question analysis:"
    )

    print(
        analysis
    )

    # ========================================================
    # CHECK ANSWERABILITY
    # ========================================================

    if isinstance(
        analysis,
        dict
    ):

        answerable = analysis.get(
            "answerable",
            False
        )

        reason = analysis.get(
            "reason",
            ""
        )

    else:

        answerable = (
            "UNSUPPORTED"
            not in str(
                analysis
            ).upper()
        )

        reason = str(
            analysis
        )

    if not answerable:

        print(
            "\n❌ Question cannot be answered."
        )

        print(
            reason
        )

        return None

    print(
        "\n✅ Question can be answered."
    )

    # ========================================================
    # GENERATE SQL
    # ========================================================

    print(
        "\n⚙️ Generating SQL..."
    )

    try:

        sql = generate_sql(

            question,

            selected_tables,

            user_email

        )

    except Exception as e:

        print(
            f"❌ SQL generation failed: {e}"
        )

        return None

    print(
        "\nGenerated SQL:"
    )

    print(
        sql
    )

    # ========================================================
    # VALIDATE SQL
    # ========================================================

    print(
        "\n🔐 Validating generated SQL..."
    )

    try:

        validation = validate_sql(
            sql
        )

    except Exception as e:

        print(
            f"❌ SQL validation failed: {e}"
        )

        return None

    if not validation.get(
        "valid",
        False
    ):

        print(
            "❌ SQL validation failed."
        )

        for error in validation.get(
            "errors",
            []
        ):

            print(
                f"• {error}"
            )

        return None

    print(
        "✅ SQL validation passed."
    )

    # ========================================================
    # EXECUTE SQL
    # ========================================================

    print(
        "\n🗄️ Executing query..."
    )

    result = execute_sql(
        sql
    )

    if result is None:

        return None

    if result.empty:

        print(
            "\n⚠️ No results found."
        )

        return None

    # ========================================================
    # DISPLAY RESULT
    # ========================================================

    print(
        "\n📊 RAW RESULT:"
    )

    print(
        result.to_string(
            index=False
        )
    )

    # ========================================================
    # CHART
    # ========================================================

    print(
        "\n📊 Generating chart..."
    )

    try:

        chart_result = create_chart(

            result,

            title=question

        )

        if chart_result is not None:

            print(
                "✅ Chart generated successfully."
            )

    except Exception as e:

        print(
            f"⚠️ Chart generation failed: {e}"
        )

    # ========================================================
    # BUSINESS EXPLANATION
    # ========================================================

    print(
        "\n🧠 Generating business explanation..."
    )

    answer = generate_business_answer(

        question,

        result,

        memory_context

    )

    # ========================================================
    # SAVE CHAT MEMORY
    # ========================================================

    print(
        "\n💾 Saving conversation..."
    )

    try:

        save_chat(

            user_email=user_email,

            dataset_name=dataset_name,

            question=question,

            answer=answer,

            sql_query=sql

        )

        print(
            "✅ Conversation saved."
        )

    except Exception as e:

        print(
            f"⚠️ Could not save conversation: {e}"
        )

    # ========================================================
    # DISPLAY FINAL ANSWER
    # ========================================================

    print(
        "\n" + "=" * 60
    )

    print(
        "📈 BUSINESS ANSWER"
    )

    print("=" * 60)

    print(
        answer
    )

    print(
        "=" * 60
    )

    return {

        "question":
            question,

        "sql":
            sql,

        "result":
            result,

        "answer":
            answer,

        "memory":
            memory_context

    }


# ============================================================
# MAIN PROGRAM
# ============================================================

if __name__ == "__main__":

    print(
        "\n🧠 AI BUSINESS ANALYST"
    )

    print(
        "Natural-language business intelligence"
    )

    print(
        "-" * 60
    )

    user_email = input(
        "Enter user email: "
    ).strip()

    if not user_email:

        print(
            "❌ Email is required."
        )

        exit()

    dataset_name = input(
        "Enter dataset name: "
    ).strip()

    if not dataset_name:

        print(
            "❌ Dataset name is required."
        )

        exit()

    question = input(
        "Ask a business question: "
    ).strip()

    if not question:

        print(
            "❌ Question is required."
        )

        exit()

    analyze_business_question(

        question=question,

        user_email=user_email,

        dataset_name=dataset_name

    )