from sqlalchemy import text
from database import engine


def get_all_columns():

    query = """
    SELECT
        table_name,
        column_name
    FROM information_schema.columns
    WHERE table_schema = 'public'
    ORDER BY table_name;
    """

    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall()



def get_primary_key_candidates(columns):

    primary_keys = []

    for table, column in columns:

        if column.endswith("_id"):

            # likely primary key
            if (
                column == table.rstrip("s") + "_id"
                or column == table.replace("_dataset","").rstrip("s") + "_id"
            ):
                primary_keys.append(
                    (table, column)
                )

    return primary_keys



def detect_relationships():

    columns = get_all_columns()

    primary_keys = get_primary_key_candidates(columns)


    relationships = []


    for pk_table, pk_column in primary_keys:

        for table, column in columns:


            if table == pk_table:
                continue


            if column == pk_column:


                relationship = {
                    "from_table": table,
                    "from_column": column,
                    "to_table": pk_table,
                    "to_column": pk_column
                }


                relationships.append(
                    relationship
                )


    return relationships