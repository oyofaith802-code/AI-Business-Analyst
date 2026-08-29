from ollama import chat
from schema_memory import get_schema


def analyze_question(question, tables, user_email):
    """
    Analyze whether a business question can be answered
    using the selected database tables.
    """

    # --------------------------------------------------------
    # GET USER DATASET SCHEMA
    # --------------------------------------------------------

    schema = get_schema(
        user_email,
        tables
    )

    # --------------------------------------------------------
    # CHECK IF SCHEMA EXISTS
    # --------------------------------------------------------

    if not schema:
        return {
            "answerable": False,
            "reason": "No database schema was found for the selected tables.",
            "tables": tables,
            "columns": [],
            "raw_response": ""
        }

    # --------------------------------------------------------
    # AI REASONING PROMPT
    # --------------------------------------------------------

    prompt = f"""
You are a professional database analysis AI.

Your ONLY task is to determine whether a business question
can be answered using the available database schema.

DATABASE SCHEMA:

{schema}

USER QUESTION:

{question}

AVAILABLE TABLES:

{", ".join(tables)}

RULES:

1. If the required information exists in the schema, respond:

SUPPORTED

Then explain briefly why the question can be answered.

2. If the required information does NOT exist, respond:

UNSUPPORTED

Then explain:
- What information is missing.
- Which table or column would be needed.

3. Do not generate SQL.

4. Do not calculate results.

5. Do not invent columns.

6. Do not invent tables.

7. Do not assume information that does not exist.

8. Do not greet the user.

9. Do not ask questions.

10. Your first word MUST be either SUPPORTED or UNSUPPORTED.

11. If the question requires multiple tables, identify the
tables that contain the required information.

"""

    # --------------------------------------------------------
    # CALL LOCAL LLM
    # --------------------------------------------------------

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

    raw_response = response["message"]["content"].strip()

    # --------------------------------------------------------
    # DETERMINE ANSWERABILITY
    # --------------------------------------------------------

    upper_response = raw_response.upper()

    if upper_response.startswith("SUPPORTED"):
        answerable = True
    else:
        answerable = False

    # --------------------------------------------------------
    # EXTRACT REASON
    # --------------------------------------------------------

    reason = raw_response

    if answerable:
        reason = raw_response.replace(
            "SUPPORTED",
            "",
            1
        ).strip()
    else:
        reason = raw_response.replace(
            "UNSUPPORTED",
            "",
            1
        ).strip()

    # --------------------------------------------------------
    # RETURN STRUCTURED RESULT
    # --------------------------------------------------------

    return {
        "answerable": answerable,
        "reason": reason,
        "tables": tables,
        "columns": [],
        "raw_response": raw_response
    }


# ============================================================
# COMMAND LINE TEST
# ============================================================

def main():

    print("=" * 60)
    print("DATASET REASONING TEST")
    print("=" * 60)

    user_email = input(
        "Enter user email: "
    ).strip()

    question = input(
        "Ask a business question: "
    ).strip()

    tables_input = input(
        "Enter tables separated by commas: "
    ).strip()

    tables = [
        table.strip()
        for table in tables_input.split(",")
        if table.strip()
    ]

    print("\nAnalyzing question...")

    result = analyze_question(
        question,
        tables,
        user_email
    )

    print("\nQUESTION ANALYSIS:")
    print(result)


if __name__ == "__main__":
    main()