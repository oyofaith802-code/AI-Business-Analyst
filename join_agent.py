from relationship_detector import detect_relationships


def build_join_context(dataframes):

    relationships = detect_relationships(dataframes)

    if not relationships:
        return "No relationships detected."

    context = "Detected table relationships:\n\n"

    for left, right in relationships:
        context += f"{left} --> {right}\n"

    return context