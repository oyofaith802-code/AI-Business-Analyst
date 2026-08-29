import pandas as pd


def profile_dataset(df):

    profile = {}

    # =====================================================
    # DATASET INFORMATION
    # =====================================================

    profile["rows"] = len(df)

    profile["columns"] = list(df.columns)

    profile["column_count"] = len(df.columns)

    profile["missing_cells"] = int(
        df.isna().sum().sum()
    )


    # =====================================================
    # COLUMN INFORMATION
    # =====================================================

    column_info = {}


    for column in df.columns:

        series = df[column]

        data_type = str(
            series.dtype
        )

        unique_values = int(
            series.nunique(
                dropna=True
            )
        )

        missing_values = int(
            series.isna().sum()
        )

        non_null_values = int(
            series.notna().sum()
        )


        # -------------------------------------------------
        # Samples
        # -------------------------------------------------

        sample_values = (
            series
            .dropna()
            .head(5)
            .tolist()
        )


        # Convert unusual pandas values
        # into strings so the profile is safe to save.

        sample_values = [
            str(value)
            for value in sample_values
        ]


        # -------------------------------------------------
        # Basic information
        # -------------------------------------------------

        column_lower = str(
            column
        ).lower().strip()


        role = "unknown"


        # =================================================
        # DATE DETECTION
        # =================================================

        date_keywords = [
            "date",
            "time",
            "timestamp",
            "created",
            "updated",
            "datetime"
        ]


        looks_like_date = any(
            word in column_lower
            for word in date_keywords
        )


        if looks_like_date:

            role = "date"


        # =================================================
        # IDENTIFIER DETECTION
        # =================================================

        elif (
            column_lower == "id"
            or column_lower.endswith("_id")
            or column_lower.endswith("id")
        ):

            role = "identifier"


        # =================================================
        # FINANCIAL DETECTION
        # =================================================

        elif any(
            word in column_lower
            for word in [
                "price",
                "amount",
                "revenue",
                "sales",
                "profit",
                "cost",
                "income",
                "payment",
                "salary",
                "fee",
                "expense",
                "value",
                "discount",
                "tax"
            ]
        ) and pd.api.types.is_numeric_dtype(
            series
        ):

            role = "financial"


        # =================================================
        # NUMERIC DETECTION
        # =================================================

        elif pd.api.types.is_numeric_dtype(
            series
        ):

            role = "numeric"


        # =================================================
        # CATEGORY DETECTION
        # =================================================

        elif (
            series.dtype == "object"
            and unique_values <= 50
        ):

            role = "category"


        # =================================================
        # TEXT DETECTION
        # =================================================

        elif series.dtype == "object":

            role = "text"


        # =================================================
        # NUMERIC STATISTICS
        # =================================================

        statistics = {}


        if pd.api.types.is_numeric_dtype(
            series
        ):

            try:

                statistics = {

                    "min": float(
                        series.min()
                    ),

                    "max": float(
                        series.max()
                    ),

                    "average": float(
                        series.mean()
                    )

                }

            except Exception:

                statistics = {}


        # =================================================
        # SAVE COLUMN PROFILE
        # =================================================

        column_info[column] = {

            "type": data_type,

            "role": role,

            "unique_values": unique_values,

            "missing_values": missing_values,

            "non_null_values": non_null_values,

            "samples": sample_values,

            "statistics": statistics

        }


    # =====================================================
    # SAVE COLUMN INFORMATION
    # =====================================================

    profile["columns_info"] = column_info


    return profile