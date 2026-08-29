from relationship_reader import detect_relationships


def get_relationship_context():

    relationships = detect_relationships()

    text = "Database relationships:\n\n"

    for r in relationships:

        text += (
            f"{r['from_table']}."
            f"{r['from_column']} "
            f"JOIN "
            f"{r['to_table']}."
            f"{r['to_column']}\n"
        )


    return text