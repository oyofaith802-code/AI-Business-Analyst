from sql_agent import generate_sql
from schema_reader import get_table_schema
from database import run_query


def ask_business(question, table_name):

    # get table structure
    schema = get_table_schema(table_name)


    # generate SQL
    sql = generate_sql(
        question,
        table_name,
        schema
    )


    print("Generated SQL:")
    print(sql)


    # run SQL
    result = run_query(sql)


    print("\nDatabase Result:")
    print(result)


    return result