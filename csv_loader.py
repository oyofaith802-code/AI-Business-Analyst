import pandas as pd
from sqlalchemy import create_engine
import re
import uuid


import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{quote_plus(DB_PASSWORD)}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)


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