import pandas as pd


def detect_relationships(dataframes):

    relationships = []

    table_names = list(dataframes.keys())

    for i in range(len(table_names)):

        for j in range(i + 1, len(table_names)):

            table1 = table_names[i]
            table2 = table_names[j]

            df1 = dataframes[table1]
            df2 = dataframes[table2]

            common_columns = set(df1.columns).intersection(df2.columns)

            for column in common_columns:

                relationships.append(
                    (
                        f"{table1}.{column}",
                        f"{table2}.{column}"
                    )
                )

    return relationships