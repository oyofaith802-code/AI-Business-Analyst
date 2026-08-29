from database import engine
from sqlalchemy import text



def create_business_memory_table():

    query = """

    CREATE TABLE IF NOT EXISTS business_memory (

        id SERIAL PRIMARY KEY,

        user_email TEXT NOT NULL,

        table_name TEXT NOT NULL,

        metric TEXT,

        column_name TEXT,

        UNIQUE(
            user_email,
            table_name,
            metric
        )

    );

    """


    with engine.connect() as conn:

        conn.execute(
            text(query)
        )

        conn.commit()





def save_business_memory(
    user_email,
    table_name,
    metrics
):


    query = """

    INSERT INTO business_memory

    (
        user_email,
        table_name,
        metric,
        column_name
    )

    VALUES

    (
        :user_email,
        :table_name,
        :metric,
        :column_name
    )


    ON CONFLICT
    (
        user_email,
        table_name,
        metric
    )

    DO UPDATE SET

    column_name =
    EXCLUDED.column_name;

    """



    with engine.connect() as conn:


        for metric, column in metrics.items():

            conn.execute(
                text(query),
                {

                "user_email": user_email,

                "table_name": table_name,

                "metric": metric,

                "column_name": column

                }
            )


        conn.commit()