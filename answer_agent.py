# ============================================================
# AI BUSINESS ANALYST - ANSWER AGENT
# ============================================================

from ollama import chat

from chat_memory import (
    get_chat_history,
)


# ============================================================
# BUILD PREVIOUS CONVERSATION
# ============================================================

def build_previous_conversation(
    user_email,
    dataset_name,
    limit=10,
):

    try:

        history = get_chat_history(
            user_email,
            dataset_name,
            limit=limit,
        )

    except Exception as e:

        print(
            f"⚠️ Could not load chat history: {e}"
        )

        return "No previous conversation."


    if not history:

        return "No previous conversation."


    parts = []


    for item in reversed(history):

        question = item.get(
            "question",
            "",
        )

        answer = item.get(
            "answer",
            "",
        )

        if not question:

            continue


        parts.append(
            f"""
Previous user question:
{question}

Previous AI answer:
{answer}
"""
        )


    if not parts:

        return "No previous conversation."


    return "\n".join(parts)


# ============================================================
# BUILD ANSWER PROMPT
# ============================================================

def build_answer_prompt(
    question,
    result_text,
    dataset_name,
    previous_conversation,
):

    prompt = f"""
You are a professional AI Business Analyst.

Your job is to explain database results to a business user.

CURRENT DATASET:
{dataset_name}

PREVIOUS CONVERSATION:
{previous_conversation}

CURRENT USER QUESTION:
{question}

CURRENT DATABASE RESULT:
{result_text}


IMPORTANT RULES:

1. Answer the user's question directly.

2. Use ONLY information contained in the
   current database result and relevant
   previous conversation.

3. Never invent numbers.

4. Never invent business facts.

5. Never create values that are not present
   in the database result.

6. Preserve category names, product names,
   customer names, regions and other labels.

7. If the user asks a follow-up question such as:

   "Which one?"
   "Which is better?"
   "Why?"
   "What about the other one?"
   "Compare them."
   "Show me more."

   use the previous conversation to understand
   what the user means.

8. If the current result does not contain
   enough information to answer the question,
   clearly say that the available data is
   insufficient.

9. If the result contains rankings, identify
   the relevant highest or lowest result.

10. If the result contains multiple categories,
    compare them when relevant.

11. Do not repeat the entire database result
    unnecessarily.

12. Keep the answer concise and useful.

13. Use the same language as the user's question.

14. Give one useful business insight based only
    on the available data.


RESPONSE FORMAT:

Answer:

Give the direct answer here.

Business insight:

Give one useful insight here.
"""

    return prompt


# ============================================================
# GENERATE BUSINESS ANSWER
# ============================================================

def generate_business_answer(
    question,
    result,
    user_email,
    dataset_name,
):

    if not question:

        raise ValueError(
            "Question is required."
        )


    if result is None:

        raise ValueError(
            "Database result is required."
        )


    # --------------------------------------------------------
    # CONVERT RESULT TO TEXT
    # --------------------------------------------------------

    try:

        result_text = result.to_string(
            index=False
        )

    except Exception:

        result_text = str(
            result
        )


    if not result_text.strip():

        return (
            "The database returned no usable result."
        )


    # --------------------------------------------------------
    # LOAD CHAT MEMORY
    # --------------------------------------------------------

    previous_conversation = (
        build_previous_conversation(
            user_email=user_email,
            dataset_name=dataset_name,
            limit=10,
        )
    )


    # --------------------------------------------------------
    # BUILD PROMPT
    # --------------------------------------------------------

    prompt = build_answer_prompt(
        question=question,
        result_text=result_text,
        dataset_name=dataset_name,
        previous_conversation=previous_conversation,
    )


    # --------------------------------------------------------
    # CALL OLLAMA
    # --------------------------------------------------------

    try:

        response = chat(

            model="llama3.2",

            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],

            options={
                "temperature": 0,
            },
        )

    except Exception as e:

        raise RuntimeError(
            f"Ollama answer generation failed: {e}"
        )


    # --------------------------------------------------------
    # EXTRACT RESPONSE
    # --------------------------------------------------------

    try:

        answer = response[
            "message"
        ][
            "content"
        ]

    except Exception:

        raise RuntimeError(
            "Ollama returned an unexpected response."
        )


    answer = str(
        answer
    ).strip()


    if not answer:

        raise RuntimeError(
            "AI returned an empty business answer."
        )


    return answer


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "============================================================"
    )

    print(
        "AI BUSINESS ANALYST - ANSWER AGENT TEST"
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
        "Enter business question: "
    ).strip()


    print()
    print(
        "Enter the database result."
    )
    print(
        "Example: Electronics 270000"
    )
    print()


    result_text = input(
        "Database result: "
    ).strip()


    class SimpleResult:

        def __init__(
            self,
            text,
        ):

            self.text = text


        def to_string(
            self,
            index=False,
        ):

            return self.text


    result = SimpleResult(
        result_text
    )


    print()
    print(
        "Generating business answer..."
    )


    try:

        answer = generate_business_answer(
            question=question,
            result=result,
            user_email=email,
            dataset_name=dataset,
        )


        print()
        print(
            "============================================================"
        )

        print(
            "BUSINESS ANSWER"
        )

        print(
            "============================================================"
        )

        print(
            answer
        )

        print()
        print(
            "✅ Answer agent test completed."
        )


    except Exception as e:

        print()
        print(
            "❌ Answer generation failed:"
        )

        print(
            e
        )
