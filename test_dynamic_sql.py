from sql_agent import generate_sql


sql = generate_sql(
    "How many orders were delivered?",
    "olist_orders_dataset"
)


print("Generated SQL:")
print(sql)