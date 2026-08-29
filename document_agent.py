from ollama import chat

from document_memory import (
    get_document_context,
    get_document_sources,
)


# ============================================================
# ANSWER DOCUMENT QUESTION
# ============================================================

def answer_document_question(
    user_email,
    question,
):

    # --------------------------------------------------------
    # Get relevant document content
    # --------------------------------------------------------

    context = get_document_context(
        user_email,
        question,
        limit=5,
    )

    # --------------------------------------------------------
    # No relevant document found
    # --------------------------------------------------------

    if not context:

        return (
            "I could not find relevant information "
            "in your uploaded documents."
        )


    # --------------------------------------------------------
    # Ask Ollama to answer using ONLY the documents
    # --------------------------------------------------------

    prompt = f"""
You are an AI business document analyst.

Answer the user's question using ONLY the information
contained in the uploaded document context below.

Do not invent information.

If the answer is clearly stated in the document,
give the direct answer.

Keep the answer concise and business-focused.

DOCUMENT CONTEXT:
{context}

USER QUESTION:
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


        answer = response["message"]["content"].strip()


    except Exception as e:

        return (
            f"Document AI error: {str(e)}"
        )


    # --------------------------------------------------------
    # Get sources
    # --------------------------------------------------------

    sources = get_document_sources(
        user_email,
        question,
        limit=5,
    )


    # --------------------------------------------------------
    # Add source citation
    # --------------------------------------------------------

    if sources:

        source_lines = []

        seen = set()

        for source in sources:

            filename = source["filename"]

            page = source["page"]

            source_key = (
                filename,
                page,
            )

            if source_key in seen:
                continue

            seen.add(
                source_key
            )

            source_lines.append(
                f"Source: {filename} — Page {page}"
            )


        if source_lines:

            answer = (
                answer
                + "\n\n"
                + "\n".join(source_lines)
            )


    return answer