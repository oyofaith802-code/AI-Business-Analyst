import pandas as pd
from sqlalchemy import create_engine
import re
import uuid


DATABASE_URL = "postgresql://postgres:2005Solomon%40@localhost:5432/business_ai"


engine = create_engine(
    DATABASE_URL
)



# ---------------------------------------
# Clean Table Name
# ---------------------------------------

def clean_table_name(filename):

    name = filename.replace(".csv", "")


    name = re.sub(
        r'[^a-zA-Z0-9_]',
        '_',
        name
    )


    return name.lower()



# ---------------------------------------
# Detect Date Columns
# ---------------------------------------

def convert_dates(df):

    for col in df.columns:


        column_name = col.lower()


        if (
            "date" in column_name
            or "time" in column_name
        ):


            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            )


    return df



# ---------------------------------------
# Load CSV To Database
# ---------------------------------------

def load_csv_to_database(file, user_email):


    # Streamlit uploaded file

    if not isinstance(file, str):

        df = pd.read_csv(
            file
        )

        filename = file.name



    # Normal file path

    else:

        df = pd.read_csv(
            file
        )

        filename = file.split("\\")[-1]



    # Convert date columns

    df = convert_dates(
        df
    )



    # Clean table name

    base_name = clean_table_name(
        filename
    )



    # Create unique table

    user_id = user_email.split("@")[0]

    unique_id = str(uuid.uuid4())[:8]


    table_name = (
        f"{user_id}_{base_name}_{unique_id}"
    )



    # Save to PostgreSQL

    df.to_sql(

        table_name,

        engine,

        if_exists="replace",

        index=False

    )


    return table_name, df