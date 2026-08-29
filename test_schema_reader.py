from schema_reader import get_table_schema


table = "olist_orders_dataset"


schema = get_table_schema(table)


print("Table structure:")

for column in schema:
    print(column)