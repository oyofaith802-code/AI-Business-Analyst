import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
from sql_generator import generate_sql


# ==============================
# LOAD ENVIRONMENT VARIABLES
# ==============================

load_dotenv()


# ==============================
# DATABASE CONFIGURATION
# ==============================

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT")
}


# ==============================
# CONNECT TO DATABASE
# ==============================

def get_connection():

    return psycopg2.connect(
        host=DB_CONFIG["host"],
        database=DB_CONFIG["database"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"],
        port=DB_CONFIG["port"]
    )


# ==============================
# EXECUTE SQL
# ==============================

def execute_sql(sql):

    connection = None

    try:

        connection = get_connection()

        df = pd.read_sql_query(sql, connection)

        return df

    except Exception as e:

        print("\n❌ SQL EXECUTION ERROR")
        print(e)

        return None

    finally:

        if connection:
            connection.close()


# ==============================
# MAIN
# ==============================

if __name__ == "__main__":

    print("\n🤖 AI BUSINESS ANALYST - SQL EXECUTOR")

    question = input("\nAsk a business question: ")

    print("\n🧠 Generating SQL...")

    try:

        sql = generate_sql(question)

        print("\nGenerated SQL:")
        print(sql)

        print("\n🗄️ Executing query...")

        result = execute_sql(sql)

        if result is not None:

            print("\n✅ Query executed successfully.")

            print("\n📊 RESULT:")

            print(result.to_string(index=False))

            print("\n" + "=" * 60)

    except Exception as e:

        print("\n❌ ERROR:")
        print(e)