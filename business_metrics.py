# business_metrics.py

import pandas as pd
import numpy as np


# ============================================================
# DATE DETECTION
# ============================================================

def try_parse_date(series):
    """
    Safely determine whether a column contains date/time values.

    Works with:
    - PostgreSQL timestamps
    - CSV date strings
    - ISO dates
    - Common international date formats
    - Missing values
    """

    if series is None:
        return None

    # Already datetime
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors="coerce")

    # Remove missing values
    non_null = series.dropna()

    if len(non_null) == 0:
        return None

    # Numeric columns are normally not dates
    if pd.api.types.is_numeric_dtype(series):
        return None

    try:
        # First attempt: pandas automatic parsing
        parsed = pd.to_datetime(
            series,
            errors="coerce",
            format="mixed"
        )

    except Exception:

        try:
            # Fallback
            parsed = pd.to_datetime(
                series,
                errors="coerce"
            )

        except Exception:
            return None

    # Calculate percentage successfully parsed
    valid_count = parsed.notna().sum()
    total_count = series.notna().sum()

    if total_count == 0:
        return None

    parse_ratio = valid_count / total_count

    # Require most non-null values to look like dates
    if parse_ratio >= 0.70:
        return parsed

    return None


def is_date_column(series):
    """
    Return True if a column appears to contain dates.
    """

    parsed = try_parse_date(series)

    return parsed is not None


# ============================================================
# COLUMN CLASSIFICATION
# ============================================================

def classify_column(column_name, series):
    """
    Classify a dataframe column into a business-friendly type.
    """

    name = str(column_name).lower().strip()

    # --------------------------------------------------------
    # Empty column
    # --------------------------------------------------------

    if series.dropna().empty:
        return "text"

    # --------------------------------------------------------
    # Identifier detection
    # --------------------------------------------------------

    identifier_keywords = [
        "id",
        "_id",
        "uuid",
        "code",
        "key",
        "reference",
        "ref"
    ]

    identifier_match = any(
        keyword in name
        for keyword in identifier_keywords
    )

    if identifier_match:

        unique_ratio = (
            series.nunique(dropna=True)
            / max(series.notna().sum(), 1)
        )

        if unique_ratio >= 0.50:
            return "identifier"

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    if pd.api.types.is_numeric_dtype(series):

        # Integer-like columns with relatively few unique values
        # may represent categories.
        unique_count = series.nunique(dropna=True)

        if unique_count <= 20 and unique_count > 1:
            return "category"

        return "numeric"

    # --------------------------------------------------------
    # Boolean columns
    # --------------------------------------------------------

    if pd.api.types.is_bool_dtype(series):
        return "category"

    # --------------------------------------------------------
    # Date columns
    # --------------------------------------------------------

    if is_date_column(series):
        return "date"

    # --------------------------------------------------------
    # Category detection
    # --------------------------------------------------------

    unique_count = series.nunique(dropna=True)
    total_count = series.notna().sum()

    if total_count > 0:

        unique_ratio = unique_count / total_count

        # Low-cardinality text columns are usually categories
        if unique_count <= 50 and unique_ratio <= 0.20:
            return "category"

    # --------------------------------------------------------
    # Text
    # --------------------------------------------------------

    return "text"


def classify_columns(df):
    """
    Classify every column in a dataframe.

    Returns:

    {
        "column_name": "identifier",
        "column_name": "numeric",
        "column_name": "date",
        "column_name": "category",
        "column_name": "text"
    }
    """

    classification = {}

    if df is None or df.empty:
        return classification

    for column in df.columns:

        try:

            classification[column] = classify_column(
                column,
                df[column]
            )

        except Exception:

            classification[column] = "text"

    return classification


# ============================================================
# BUSINESS COLUMN DETECTION
# ============================================================

def detect_business_columns(df, classification):
    """
    Detect columns that may represent common business concepts.

    This is intentionally generic so that the application can
    work with datasets from different industries.
    """

    business_columns = {
        "identifiers": [],
        "dates": [],
        "categories": [],
        "numeric_measures": [],
        "revenue": [],
        "cost": [],
        "profit": [],
        "quantity": [],
        "customers": [],
        "products": [],
        "text": []
    }

    for column, column_type in classification.items():

        name = str(column).lower().strip()

        # ----------------------------------------------------
        # Identifiers
        # ----------------------------------------------------

        if column_type == "identifier":

            business_columns["identifiers"].append(column)

        # ----------------------------------------------------
        # Dates
        # ----------------------------------------------------

        elif column_type == "date":

            business_columns["dates"].append(column)

        # ----------------------------------------------------
        # Categories
        # ----------------------------------------------------

        elif column_type == "category":

            business_columns["categories"].append(column)

        # ----------------------------------------------------
        # Text
        # ----------------------------------------------------

        elif column_type == "text":

            business_columns["text"].append(column)

        # ----------------------------------------------------
        # Numeric
        # ----------------------------------------------------

        elif column_type == "numeric":

            business_columns["numeric_measures"].append(column)

        # ----------------------------------------------------
        # Revenue
        # ----------------------------------------------------

        revenue_keywords = [
            "revenue",
            "sales",
            "sale",
            "income",
            "turnover",
            "amount",
            "payment_value",
            "total_value",
            "gross_sales",
            "selling_price"
        ]

        if any(
            keyword in name
            for keyword in revenue_keywords
        ):

            if column not in business_columns["revenue"]:
                business_columns["revenue"].append(column)

        # ----------------------------------------------------
        # Cost
        # ----------------------------------------------------

        cost_keywords = [
            "cost",
            "expense",
            "expenses",
            "spending",
            "purchase_cost",
            "shipping_cost",
            "freight"
        ]

        if any(
            keyword in name
            for keyword in cost_keywords
        ):

            if column not in business_columns["cost"]:
                business_columns["cost"].append(column)

        # ----------------------------------------------------
        # Profit
        # ----------------------------------------------------

        profit_keywords = [
            "profit",
            "profit_amount",
            "net_profit",
            "gross_profit",
            "margin"
        ]

        if any(
            keyword in name
            for keyword in profit_keywords
        ):

            if column not in business_columns["profit"]:
                business_columns["profit"].append(column)

        # ----------------------------------------------------
        # Quantity
        # ----------------------------------------------------

        quantity_keywords = [
            "quantity",
            "qty",
            "units",
            "unit_count",
            "count",
            "volume"
        ]

        if any(
            keyword in name
            for keyword in quantity_keywords
        ):

            if column not in business_columns["quantity"]:
                business_columns["quantity"].append(column)

        # ----------------------------------------------------
        # Customer columns
        # ----------------------------------------------------

        customer_keywords = [
            "customer",
            "client",
            "buyer",
            "user"
        ]

        if any(
            keyword in name
            for keyword in customer_keywords
        ):

            if column not in business_columns["customers"]:
                business_columns["customers"].append(column)

        # ----------------------------------------------------
        # Product columns
        # ----------------------------------------------------

        product_keywords = [
            "product",
            "item",
            "sku",
            "stock",
            "merchandise"
        ]

        if any(
            keyword in name
            for keyword in product_keywords
        ):

            if column not in business_columns["products"]:
                business_columns["products"].append(column)

    return business_columns


# ============================================================
# MEANING DETECTION
# ============================================================

def detect_measure_meanings(df, classification):
    """
    Explain what each column appears to represent.
    """

    meanings = {}

    for column, column_type in classification.items():

        name = str(column).lower().strip()

        # Identifier
        if column_type == "identifier":

            meanings[column] = "identifier"

        # Date
        elif column_type == "date":

            meanings[column] = "date/time field"

        # Numeric
        elif column_type == "numeric":

            if any(
                word in name
                for word in [
                    "revenue",
                    "sales",
                    "amount",
                    "income",
                    "payment"
                ]
            ):

                meanings[column] = "financial measure"

            elif any(
                word in name
                for word in [
                    "cost",
                    "expense",
                    "freight"
                ]
            ):

                meanings[column] = "cost measure"

            elif any(
                word in name
                for word in [
                    "profit",
                    "margin"
                ]
            ):

                meanings[column] = "profit measure"

            elif any(
                word in name
                for word in [
                    "quantity",
                    "qty",
                    "units"
                ]
            ):

                meanings[column] = "quantity measure"

            else:

                meanings[column] = "numeric measure"

        # Category
        elif column_type == "category":

            meanings[column] = "category field"

        # Text
        else:

            meanings[column] = "text field"

    return meanings


# ============================================================
# DATASET METRICS
# ============================================================

def detect_business_metrics(df):
    """
    Generate general business/data quality metrics.

    Works with arbitrary CSV datasets.
    """

    if df is None:
        return {}

    if not isinstance(df, pd.DataFrame):
        return {}

    rows = len(df)
    columns = len(df.columns)

    try:
        unique_records = len(df.drop_duplicates())
    except Exception:
        unique_records = rows

    try:
        duplicate_rows = int(df.duplicated().sum())
    except Exception:
        duplicate_rows = 0

    try:
        missing_values = int(df.isna().sum().sum())
    except Exception:
        missing_values = 0

    classification = classify_columns(df)

    date_columns = sum(
        1
        for value in classification.values()
        if value == "date"
    )

    category_fields = sum(
        1
        for value in classification.values()
        if value == "category"
    )

    numeric_fields = sum(
        1
        for value in classification.values()
        if value == "numeric"
    )

    identifier_fields = sum(
        1
        for value in classification.values()
        if value == "identifier"
    )

    text_fields = sum(
        1
        for value in classification.values()
        if value == "text"
    )

    return {
        "Total Records": rows,
        "Columns": columns,
        "Rows": rows,
        "Unique Records": unique_records,
        "Date Columns": date_columns,
        "Category Fields": category_fields,
        "Numeric Fields": numeric_fields,
        "Identifier Fields": identifier_fields,
        "Text Fields": text_fields,
        "Missing Values": missing_values,
        "Duplicate Rows": duplicate_rows
    }


# ============================================================
# COMPLETE DATASET ANALYSIS
# ============================================================

def analyze_dataset(df):
    """
    Complete automatic dataset analysis.

    Returns:

    {
        "metrics": {...},
        "classification": {...},
        "business_columns": {...},
        "measure_meanings": {...}
    }
    """

    if df is None or not isinstance(df, pd.DataFrame):

        return {
            "metrics": {},
            "classification": {},
            "business_columns": {},
            "measure_meanings": {}
        }

    classification = classify_columns(df)

    metrics = detect_business_metrics(df)

    business_columns = detect_business_columns(
        df,
        classification
    )

    measure_meanings = detect_measure_meanings(
        df,
        classification
    )

    return {
        "metrics": metrics,
        "classification": classification,
        "business_columns": business_columns,
        "measure_meanings": measure_meanings
    }


# ============================================================
# BUSINESS SUMMARY
# ============================================================

def generate_business_summary(df):
    """
    Generate a simple human-readable summary of a dataset.
    """

    analysis = analyze_dataset(df)

    metrics = analysis["metrics"]
    business_columns = analysis["business_columns"]

    summary = []

    rows = metrics.get("Rows", 0)
    columns = metrics.get("Columns", 0)
    missing = metrics.get("Missing Values", 0)
    duplicates = metrics.get("Duplicate Rows", 0)

    summary.append(
        f"The dataset contains {rows:,} rows "
        f"and {columns} columns."
    )

    if missing > 0:

        summary.append(
            f"It contains {missing:,} missing values."
        )

    else:

        summary.append(
            "It contains no missing values."
        )

    if duplicates > 0:

        summary.append(
            f"It contains {duplicates:,} duplicate rows."
        )

    else:

        summary.append(
            "No duplicate rows were detected."
        )

    revenue = business_columns.get(
        "revenue",
        []
    )

    if revenue:

        summary.append(
            "Potential revenue fields: "
            + ", ".join(revenue)
            + "."
        )

    cost = business_columns.get(
        "cost",
        []
    )

    if cost:

        summary.append(
            "Potential cost fields: "
            + ", ".join(cost)
            + "."
        )

    profit = business_columns.get(
        "profit",
        []
    )

    if profit:

        summary.append(
            "Potential profit fields: "
            + ", ".join(profit)
            + "."
        )

    return " ".join(summary)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print(
        "business_metrics.py loaded successfully."
    )