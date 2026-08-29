from sql_agent import generate_sql
from database import run_query


def ask_business(question, table_name, user_email=None):

    sql = generate_sql(
        question,
        [table_name],
        user_email
    )

    print("Generated SQL:")
    print(sql)

    result = run_query(sql)

    print("\nDatabase Result:")
    print(result)

    return result
