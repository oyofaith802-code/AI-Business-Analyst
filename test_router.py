from business_router import business_router


questions = [
    "What is my delivery performance?",
    "What is my cancellation rate?",
    "What is my average order value?",
    "What is my revenue?"
]


for q in questions:
    print("\nQuestion:", q)
    print("Answer:", business_router(q))