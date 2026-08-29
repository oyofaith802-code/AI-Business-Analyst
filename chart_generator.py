# ============================================================
# CHART GENERATOR
# ============================================================

import os
import re

import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


# ============================================================
# CHART DIRECTORY
# ============================================================

CHART_DIR = "charts"

os.makedirs(
    CHART_DIR,
    exist_ok=True
)


# ============================================================
# SAFE FILENAME
# ============================================================

def safe_filename(text):

    """
    Convert any text into a Windows-safe filename.
    """

    text = str(text)

    # Remove Windows-invalid characters:
    # < > : " / \ | ? *

    text = re.sub(
        r'[<>:"/\\|?*]',
        "",
        text
    )

    # Replace spaces with underscores

    text = re.sub(
        r"\s+",
        "_",
        text
    )

    # Keep only safe characters

    text = re.sub(
        r"[^a-zA-Z0-9_.-]",
        "",
        text
    )

    # Remove repeated underscores

    text = re.sub(
        r"_+",
        "_",
        text
    )

    # Remove leading/trailing underscores

    text = text.strip(
        "_"
    )

    # Prevent empty filename

    if not text:

        text = "business_chart"

    return text.lower()


# ============================================================
# DETECT CHART TYPE
# ============================================================

def detect_chart_type(df):

    if df is None:
        return None

    if df.empty:
        return None

    if len(df.columns) < 2:
        return None

    x_column = df.columns[0]
    x_data = df[x_column]

    if pd.api.types.is_datetime64_any_dtype(x_data):
        return "line"

    if x_data.dtype == "object" or str(x_data.dtype).startswith("string"):
        try:
            converted = pd.to_datetime(x_data, errors="coerce")
            if converted.notna().all():
                return "line"
        except Exception:
            pass

    if pd.api.types.is_numeric_dtype(x_data):
        return "scatter"

    return "bar"


# ============================================================
# CREATE CHART
# ============================================================

def create_chart(
    df=None,
    title="Business Analysis",
    result=None,
    chart_type=None,
    x_column=None,
    y_column=None
):

    # Support both df= and result= calling styles
    if df is None:
        df = result

    if df is None:
        print("No data available for chart.")
        return None

    if df.empty:
        print("Empty dataset.")
        return None

    if len(df.columns) < 2:
        print("Not enough columns for a chart.")
        return None

    # Detect columns if they were not supplied
    if x_column is None or y_column is None:
        x_column, y_column = detect_chart_columns(df)

    if x_column is None or y_column is None:
        print("Unable to determine chart columns.")
        return None

    # Detect chart type if it was not supplied
    if chart_type is None:
        chart_type = detect_chart_type(df)

    print(f"Chart type: {chart_type}")
    print(f"X column: {x_column}")
    print(f"Y column: {y_column}")

    if chart_type is None:
        print("Unable to determine chart type.")
        return None

    chart_df = df.copy()

    # Prepare dates for line charts
    if chart_type == "line":
        try:
            chart_df[x_column] = pd.to_datetime(
                chart_df[x_column],
                errors="coerce"
            )
            chart_df = chart_df.dropna(subset=[x_column])
            chart_df = chart_df.sort_values(by=x_column)
        except Exception:
            pass

    plt.figure(figsize=(10, 6))

    try:
        if chart_type == "bar":
            plt.bar(
                chart_df[x_column].astype(str),
                chart_df[y_column]
            )
            plt.xlabel(str(x_column))
            plt.ylabel(str(y_column))
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "line":
            plt.plot(
                chart_df[x_column],
                chart_df[y_column],
                marker="o"
            )
            plt.xlabel(str(x_column))
            plt.ylabel(str(y_column))
            plt.xticks(rotation=45, ha="right")

        elif chart_type == "scatter":
            plt.scatter(
                chart_df[x_column],
                chart_df[y_column]
            )
            plt.xlabel(str(x_column))
            plt.ylabel(str(y_column))

        else:
            plt.close()
            print(f"Unsupported chart type: {chart_type}")
            return None

        plt.title(str(title))
        plt.grid(True, alpha=0.3)
        plt.tight_layout()

        filename = safe_filename(title)
        if not filename.endswith(".png"):
            filename += ".png"

        filepath = os.path.join(CHART_DIR, filename)

        plt.savefig(
            filepath,
            dpi=150,
            bbox_inches="tight"
        )
        plt.close()

        print("Chart created successfully.")
        print(f"Saved to: {filepath}")

        return filepath

    except Exception as e:
        plt.close()
        print("Chart generation failed:")
        print(e)
        return None


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "Testing automatic chart detection..."
    )


    test_data = pd.DataFrame({

        "category": [
            "Furniture",
            "Electronics"
        ],

        "total_revenue": [
            115000,
            270000
        ]

    })


    print(
        "Detected chart type:",
        detect_chart_type(
            test_data
        )
    )


    create_chart(

        test_data,

        title="Revenue by Category"
    )

# ============================================================
# DETECT CHART COLUMNS
# ============================================================

def detect_chart_columns(df):
    if df is None or df.empty or len(df.columns) < 2:
        return None, None

    return df.columns[0], df.columns[1]
