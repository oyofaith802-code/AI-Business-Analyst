from schema_memory import get_schema


schema = get_schema(
    ["orders","payments"]
)


print(schema)