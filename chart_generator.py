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

    y_column = df.columns[1]


    x_data = df[x_column]


    # --------------------------------------------------------
    # DATE / TIME DETECTION
    # --------------------------------------------------------

    if pd.api.types.is_datetime64_any_dtype(
        x_data
    ):

        return "line"


    # Try converting object columns to dates

    if (
        x_data.dtype == "object"
        or str(x_data.dtype).startswith("string")
    ):

        try:

            converted = pd.to_datetime(
                x_data,
                errors="coerce"
            )


            if converted.notna().all():

                return "line"

        except Exception:

            pass


    # --------------------------------------------------------
    # NUMERIC X COLUMN
    # --------------------------------------------------------

    if pd.api.types.is_numeric_dtype(
        x_data
    ):

        return "scatter"


    # --------------------------------------------------------
    # CATEGORICAL X COLUMN
    # --------------------------------------------------------

    return "bar"


# ============================================================
# CREATE CHART
# ============================================================

def create_chart(
    df,
    title="Business Analysis"
):

    if df is None:

        print(
            "⚠️ No data available for chart."
        )

        return None


    if df.empty:

        print(
            "⚠️ Empty dataset."
        )

        return None


    if len(df.columns) < 2:

        print(
            "⚠️ Not enough columns for a chart."
        )

        return None


    # ========================================================
    # COLUMNS
    # ========================================================

    x_column = df.columns[0]

    y_column = df.columns[1]


    # ========================================================
    # DETECT CHART
    # ========================================================

    chart_type = detect_chart_type(
        df
    )


    print(
        f"Chart type: {chart_type}"
    )

    print(
        f"X column: {x_column}"
    )

    print(
        f"Y column: {y_column}"
    )


    if chart_type is None:

        print(
            "⚠️ Unable to determine chart type."
        )

        return None


    # ========================================================
    # PREPARE DATA
    # ========================================================

    chart_df = df.copy()


    # Convert date column when appropriate

    if chart_type == "line":

        try:

            chart_df[x_column] = pd.to_datetime(
                chart_df[x_column]
            )

            chart_df = chart_df.sort_values(
                by=x_column
            )

        except Exception:

            pass


    # ========================================================
    # CREATE FIGURE
    # ========================================================

    plt.figure(
        figsize=(10, 6)
    )


    # ========================================================
    # BAR CHART
    # ========================================================

    if chart_type == "bar":

        plt.bar(

            chart_df[x_column].astype(str),

            chart_df[y_column]
        )

        plt.xlabel(
            x_column
        )

        plt.ylabel(
            y_column
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )


    # ========================================================
    # LINE CHART
    # ========================================================

    elif chart_type == "line":

        plt.plot(

            chart_df[x_column],

            chart_df[y_column],

            marker="o"
        )

        plt.xlabel(
            x_column
        )

        plt.ylabel(
            y_column
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )


    # ========================================================
    # SCATTER CHART
    # ========================================================

    elif chart_type == "scatter":

        plt.scatter(

            chart_df[x_column],

            chart_df[y_column]
        )

        plt.xlabel(
            x_column
        )

        plt.ylabel(
            y_column
        )


    # ========================================================
    # UNKNOWN CHART
    # ========================================================

    else:

        plt.close()

        print(
            f"⚠️ Unsupported chart type: {chart_type}"
        )

        return None


    # ========================================================
    # TITLE
    # ========================================================

    plt.title(
        str(title)
    )


    # ========================================================
    # GRID
    # ========================================================

    plt.grid(
        True,
        alpha=0.3
    )


    # ========================================================
    # LAYOUT
    # ========================================================

    plt.tight_layout()


    # ========================================================
    # SAFE FILE NAME
    # ========================================================

    filename = safe_filename(
        title
    )


    if not filename.endswith(
        ".png"
    ):

        filename += ".png"


    filepath = os.path.join(

        CHART_DIR,

        filename
    )


    # ========================================================
    # SAVE
    # ========================================================

    try:

        plt.savefig(
            filepath,
            dpi=150,
            bbox_inches="tight"
        )

        plt.close()


        print(
            "✅ Chart created successfully."
        )

        print(
            f"📊 Saved to: {filepath}"
        )


        return filepath


    except Exception as e:

        plt.close()

        print(
            "\n⚠️ Chart generation failed:"
        )

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