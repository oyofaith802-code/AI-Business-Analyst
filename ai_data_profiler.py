from llm import ask_ai
from data_understanding import analyze_table



def create_business_profile(table_name):

    schema = analyze_table(table_name)


    prompt = f"""
You are a business data analyst.

Analyze this database table.

{schema}


Explain:

1. What this dataset represents.
2. What each important column means.
3. What business questions can be answered.
4. Suggest useful KPIs.


Keep the answer clear and business friendly.
"""


    result = ask_ai(prompt)


    return result