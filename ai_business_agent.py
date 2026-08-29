from sql_agent import generate_sql
from database import run_query


def ask_business(
    question,
    tables,
    user_email=None
):

    sql = generate_sql(
        question,
        tables,
        user_email
    )

    print("Generated SQL:")
    print(sql)

    result = run_query(sql)

    print("Database Result:")
    print(result)

    return result
