from relationship_reader import detect_relationships


relationships = detect_relationships()


print("\nDetected Relationships:\n")


for r in relationships:

    print(
        f"{r['from_table']}.{r['from_column']} "
        f"--> "
        f"{r['to_table']}.{r['to_column']}"
    )