import re
from datetime import datetime

import pandas as pd

from dataset_ingestion import (
    clean_email,
    clean_column_names,
    detect_date_columns,
    profile_dataset,
    save_dataset_to_database,
    verify_database_table,
    save_schema_memory,
    save_dataset_memory_data,
)


# ============================================================
# CLEAN MANUAL DATASET NAME
# ============================================================

def clean_manual_dataset_name(name):

    name = str(name).strip().lower()

    name = re.sub(
        r"[^a-zA-Z0-9_]",
        "_",
        name
    )

    name = re.sub(
        r"_+",
        "_",
        name
    )

    name = name.strip("_")

    if not name:
        name = "manual_data"

    if name[0].isdigit():
        name = "manual_" + name

    return name[:40]


# ============================================================
# CREATE UNIQUE TABLE NAME
# ============================================================

def create_manual_table_name(
    dataset_name,
    user_email
):

    dataset_name = clean_manual_dataset_name(
        dataset_name
    )

    email_part = clean_manual_dataset_name(
        user_email.split("@")[0]
    )

    timestamp = datetime.now().strftime(
        "%Y%m%d%H%M%S"
    )

    return (
        f"manual_{email_part}_{dataset_name}_{timestamp}"
    )[:60]


# ============================================================
# INGEST DATAFRAME
# ============================================================

def ingest_manual_dataframe(
    dataframe,
    user_email,
    dataset_name="manual_data"
):

    # --------------------------------------------------------
    # VALIDATE EMAIL
    # --------------------------------------------------------

    user_email = clean_email(
        user_email
    )

    if not user_email:

        raise ValueError(
            "User email cannot be empty."
        )

    # --------------------------------------------------------
    # VALIDATE DATAFRAME
    # --------------------------------------------------------

    if dataframe is None:

        raise ValueError(
            "No data was provided."
        )

    if not isinstance(
        dataframe,
        pd.DataFrame
    ):

        raise TypeError(
            "Data must be provided as a pandas DataFrame."
        )

    dataframe = dataframe.copy()

    # --------------------------------------------------------
    # REMOVE EMPTY ROWS
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        how="all"
    )

    # --------------------------------------------------------
    # REMOVE EMPTY COLUMNS
    # --------------------------------------------------------

    dataframe = dataframe.dropna(
        axis=1,
        how="all"
    )

    if dataframe.empty:

        raise ValueError(
            "The dataset is empty."
        )

    # --------------------------------------------------------
    # CLEAN COLUMN NAMES
    # --------------------------------------------------------

    dataframe = clean_column_names(
        dataframe
    )

    # --------------------------------------------------------
    # DATE DETECTION
    # --------------------------------------------------------

    dataframe, date_columns = (
        detect_date_columns(
            dataframe
        )
    )

    # --------------------------------------------------------
    # PROFILE
    # --------------------------------------------------------

    profile = profile_dataset(
        dataframe,
        date_columns
    )

    # --------------------------------------------------------
    # TABLE NAME
    # --------------------------------------------------------

    table_name = create_manual_table_name(
        dataset_name,
        user_email
    )

    # --------------------------------------------------------
    # SAVE DATABASE
    # --------------------------------------------------------

    save_dataset_to_database(
        dataframe,
        table_name
    )

    # --------------------------------------------------------
    # VERIFY DATABASE
    # --------------------------------------------------------

    row_count = verify_database_table(
        table_name
    )

    # --------------------------------------------------------
    # SAVE SCHEMA MEMORY
    # --------------------------------------------------------

    save_schema_memory(
        user_email,
        table_name
    )

    # --------------------------------------------------------
    # SAVE DATASET MEMORY
    # --------------------------------------------------------

    save_dataset_memory_data(
        user_email,
        table_name,
        profile
    )

    # --------------------------------------------------------
    # RESULT
    # --------------------------------------------------------

    return {
        "table_name": table_name,
        "rows": row_count,
        "columns": len(
            dataframe.columns
        ),
        "date_columns": date_columns,
        "profile": profile,
        "dataframe": dataframe,
    }