from ai_business_agent import ask_business


questions = [
    "How many customers do we have?",
    "What is the average payment amount?",
    "How many orders were canceled?",
    "What are the top 5 highest payment values?",
    "How many products are in our database?"
]


for question in questions:
    print("\nQUESTION:")
    print(question)

    answer = ask_business(question)

    print("\nANSWER:")
    print(answer)

    print("-" * 50)