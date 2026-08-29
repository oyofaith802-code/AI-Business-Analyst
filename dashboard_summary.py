import pandas as pd


def generate_dashboard(df):

    summary = {}

    summary["Rows"] = len(df)

    summary["Columns"] = len(df.columns)

    summary["Missing Values"] = int(df.isnull().sum().sum())

    numeric = df.select_dtypes(include="number")

    if not numeric.empty:
        summary["Numeric Columns"] = list(numeric.columns)

        summary["Totals"] = {
            col: float(numeric[col].sum())
            for col in numeric.columns
        }

    return summary