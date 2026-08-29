from ai_business_agent import ask_business

questions = [
    ("How many customers do we have?", ["customers"]),
    ("What is the average payment amount?", ["payments"]),
    ("How many orders were canceled?", ["orders"]),
    ("What are the top 5 highest payment values?", ["payments"]),
    ("How many products are in our database?", ["products"]),
]

for question, tables in questions:
    print("\\nQUESTION:")
    print(question)

    answer = ask_business(
        question,
        tables,
        "test@example.com"
    )

    print("\\nANSWER:")
    print(answer)
    print("-" * 50)
