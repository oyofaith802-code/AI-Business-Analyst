from answer_agent import generate_business_answer


question = "How many orders were delivered?"


result = [(96478,)]


answer = generate_business_answer(
    question,
    result
)


print("Business Answer:")
print(answer)