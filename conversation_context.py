from memory import get_previous_chats


def build_conversation_context(session_id):

    history = get_previous_chats(session_id)

    if not history:
        return ""

    context = "Previous conversation:\n\n"

    # Oldest first
    for question, answer in reversed(history):

        context += f"User: {question}\n"
        context += f"Assistant: {answer}\n\n"

    return context