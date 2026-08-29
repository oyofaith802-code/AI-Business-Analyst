from llm import ask_ai


def generate_insights(context):

    prompt = f"""

You are a business analyst.

Analyze this business dataset information:

{context}


Generate:

1. Important business findings
2. Trends
3. Possible problems
4. Recommendations


Keep the answer simple and useful.

"""


    response = ask_ai(prompt)

    return response