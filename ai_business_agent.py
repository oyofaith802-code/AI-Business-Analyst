from sql_agent import generate_sql
from database import run_query


def ask_business(question):

    sql = generate_sql(question)

    print("Generated SQL:")
    print(sql)

    result = run_query(sql)

    print("Database Result:")
    print(result)

    return result


answer = ask_business(
    "How many delivered orders do we have?"
)

print(answer)