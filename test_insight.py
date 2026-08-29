from insight_agent import generate_insights


context = """

Dataset:
Sales

Columns:

date
product
sales
quantity

"""


result = generate_insights(context)

print(result)