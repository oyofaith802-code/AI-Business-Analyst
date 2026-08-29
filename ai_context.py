from schema_reader import get_table_schema
from data_preview import get_table_preview


def build_ai_context(table_name):

    schema = get_table_schema(table_name)

    preview = get_table_preview(table_name)


    schema_text = "\n".join(
        [
            f"{column} ({data_type})"
            for column, data_type in schema
        ]
    )


    context = f"""
Table name:
{table_name}


Columns:
{schema_text}


Sample data:
{preview.to_string(index=False)}
"""


    return context