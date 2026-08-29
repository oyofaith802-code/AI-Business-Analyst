# ============================================================
# DATASET PROFILING ENGINE
# ============================================================

import pandas as pd


# ============================================================
# KEYWORD DEFINITIONS
# ============================================================

COLUMN_KEYWORDS = {

    "revenue": [
        "revenue",
        "sales",
        "sale_amount",
        "sales_amount",
        "total_sales",
        "total_revenue",
        "income",
        "turnover",
        "amount"
    ],

    "cost": [
        "cost",
        "expense",
        "expenses",
        "cost_price",
        "purchase_cost"
    ],

    "profit": [
        "profit",
        "gross_profit",
        "net_profit",
        "profit_amount"
    ],

    "quantity": [
        "quantity",
        "qty",
        "units",
        "units_sold",
        "volume"
    ],

    "product": [
        "product",
        "product_name",
        "item",
        "item_name",
        "sku"
    ],

    "category": [
        "category",
        "product_category",
        "type",
        "segment"
    ],

    "customer": [
        "customer",
        "customer_id",
        "customer_name",
        "buyer",
        "client"
    ],

    "order": [
        "order",
        "order_id",
        "invoice",
        "invoice_id",
        "transaction",
        "transaction_id"
    ],

    "date": [
        "date",
        "order_date",
        "sale_date",
        "transaction_date",
        "created_at",
        "timestamp",
        "datetime"
    ],

    "currency": [
        "currency",
        "currency_code",
        "currency_type"
    ]
}


# ============================================================
# NORMALIZE COLUMN NAME
# ============================================================

def normalize_column_name(column):

    return (
        str(column)
        .strip()
        .lower()
        .replace(" ", "_")
        .replace("-", "_")
    )


# ============================================================
# DETECT COLUMN ROLE
# ============================================================

def detect_column_role(column):

    normalized = normalize_column_name(
        column
    )

    # Exact matches first

    for role, keywords in COLUMN_KEYWORDS.items():

        if normalized in keywords:

            return role


    # Partial matches

    for role, keywords in COLUMN_KEYWORDS.items():

        for keyword in keywords:

            if keyword in normalized:

                return role


    return None


# ============================================================
# PROFILE COLUMNS
# ============================================================

def profile_columns(df):

    profiles = []

    for column in df.columns:

        series = df[column]

        role = detect_column_role(
            column
        )


        profiles.append({

            "column": str(column),

            "dtype": str(
                series.dtype
            ),

            "role": role,

            "missing": int(
                series.isna().sum()
            ),

            "unique_values": int(
                series.nunique(
                    dropna=True
                )
            )

        })


    return profiles


# ============================================================
# DETECT BUSINESS METRICS
# ============================================================

def detect_business_metrics(df):

    metrics = {}


    for column in df.columns:

        role = detect_column_role(
            column
        )


        if role == "revenue":

            metrics["revenue_column"] = column


        elif role == "cost":

            metrics["cost_column"] = column


        elif role == "profit":

            metrics["profit_column"] = column


        elif role == "quantity":

            metrics["quantity_column"] = column


        elif role == "customer":

            metrics["customer_column"] = column


        elif role == "order":

            metrics["order_column"] = column


        elif role == "product":

            metrics["product_column"] = column


        elif role == "category":

            metrics["category_column"] = column


        elif role == "date":

            metrics["date_column"] = column


        elif role == "currency":

            metrics["currency_column"] = column


    return metrics


# ============================================================
# DETECT CURRENCY
# ============================================================

def detect_currency(df, currency_column=None):

    if currency_column is None:

        return None


    if currency_column not in df.columns:

        return None


    values = (
        df[currency_column]
        .dropna()
        .astype(str)
        .str.upper()
        .str.strip()
        .unique()
    )


    if len(values) == 0:

        return None


    # Common ISO currency codes

    known_currencies = {

        "USD",
        "EUR",
        "GBP",
        "NGN",
        "CAD",
        "AUD",
        "JPY",
        "CNY",
        "INR",
        "ZAR",
        "GHS",
        "KES",
        "AED",
        "SAR",
        "CHF",
        "BRL",
        "MXN"
    }


    detected = [

        value

        for value in values

        if value in known_currencies

    ]


    if detected:

        return detected


    return None


# ============================================================
# NUMERIC SUMMARY
# ============================================================

def numeric_summary(df):

    summary = {}


    numeric_columns = df.select_dtypes(
        include="number"
    ).columns


    for column in numeric_columns:

        series = df[column]


        summary[str(column)] = {

            "sum": float(
                series.sum()
            ),

            "average": float(
                series.mean()
            ),

            "minimum": float(
                series.min()
            ),

            "maximum": float(
                series.max()
            )

        }


    return summary


# ============================================================
# DATASET PROFILE
# ============================================================

def profile_dataset(df):

    if df is None:

        raise ValueError(
            "Dataset cannot be None."
        )


    if not isinstance(
        df,
        pd.DataFrame
    ):

        raise TypeError(
            "Expected a pandas DataFrame."
        )


    metrics = detect_business_metrics(
        df
    )


    currency_column = metrics.get(
        "currency_column"
    )


    profile = {

        "rows": int(
            len(df)
        ),

        "columns": int(
            len(df.columns)
        ),

        "column_names": [
            str(column)
            for column in df.columns
        ],

        "column_profiles":
            profile_columns(df),

        "business_metrics":
            metrics,

        "currency":
            detect_currency(
                df,
                currency_column
            ),

        "numeric_summary":
            numeric_summary(df)

    }


    return profile


# ============================================================
# PRINT PROFILE
# ============================================================

def print_profile(profile):

    print(
        "\n" + "=" * 60
    )

    print(
        "📊 DATASET PROFILE"
    )

    print(
        "=" * 60
    )


    print(
        f"Rows: {profile['rows']}"
    )

    print(
        f"Columns: {profile['columns']}"
    )


    print(
        "\n📋 Columns:"
    )


    for column in profile[
        "column_profiles"
    ]:

        role = column[
            "role"
        ]

        if role:

            print(
                f"• {column['column']} "
                f"→ {role}"
            )

        else:

            print(
                f"• {column['column']}"
            )


    print(
        "\n💼 Business metrics:"
    )


    metrics = profile[
        "business_metrics"
    ]


    if metrics:

        for key, value in metrics.items():

            print(
                f"• {key}: {value}"
            )

    else:

        print(
            "• No standard business metrics detected."
        )


    print(
        "\n💱 Currency:"
    )


    currency = profile[
        "currency"
    ]


    if currency:

        print(
            f"• {currency}"
        )

    else:

        print(
            "• No currency column detected."
        )


    print(
        "\n" + "=" * 60
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_data = pd.DataFrame({

        "date": [
            "2026-01-01",
            "2026-01-15",
            "2026-02-01"
        ],

        "product": [
            "Laptop",
            "Phone",
            "Tablet"
        ],

        "category": [
            "Electronics",
            "Electronics",
            "Electronics"
        ],

        "revenue": [
            150000,
            120000,
            115000
        ],

        "quantity": [
            2,
            3,
            2
        ],

        "currency": [
            "USD",
            "USD",
            "USD"
        ]

    })


    profile = profile_dataset(
        test_data
    )


    print_profile(
        profile
    )