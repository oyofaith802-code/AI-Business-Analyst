from database import engine
from schema_memory import save_schema

import pandas as pd


tables = [
    "customers",
    "orders",
    "products",
    "payments",
    "order_items",
    "reviews"
]


for table in tables:

    print("Processing:", table)


    columns = pd.read_sql(
        f"""
        SELECT 
            column_name,
            data_type

        FROM information_schema.columns

        WHERE table_name = '{table}';
        """,
        engine
    )


    schema_text = "\n".join(
        [
            f"{row.column_name}: {row.data_type}"
            for _, row in columns.iterrows()
        ]
    )


    save_schema(
        table,
        schema_text
    )


    print(
        f"Saved {table}"
    )


print("Schema memory updated successfully")