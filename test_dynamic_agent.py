from dynamic_agent import ask_business


result = ask_business(
    "How many orders are delivered?",
    "olist_orders_dataset"
)


print("\nFinal Result:")
print(result)