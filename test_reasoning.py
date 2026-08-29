from dataset_reasoning import analyze_question


result = analyze_question(
    "What is my total revenue?",
    ["orders","payments"]
)


print(result)