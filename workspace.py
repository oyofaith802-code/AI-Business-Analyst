import re
import pandas as pd

from database import engine
from sqlalchemy import text


# ============================================================
# CLEAN TABLE NAME
# ============================================================

def clean_table_name(filename):

    name = str(filename)

    name = re.sub(
        r"\.(xlsx|xls)$",
        "",
        name,
        flags=re.IGNORECASE
    )

    name = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        name
    )

    name = re.sub(
        r"_+",
        "_",
        name
    )

    name = name.strip("_").lower()

    if not name:
        name = "uploaded_data"

    if name[0].isdigit():
        name = "table_" + name

    return name


# ============================================================
# CLEAN COLUMN NAME
# ============================================================

def clean_column_name(column):

    column = str(column)

    column = column.strip().lower()

    column = re.sub(
        r"[^a-zA-Z0-9_]+",
        "_",
        column
    )

    column = re.sub(
        r"_+",
        "_",
        column
    )

    column = column.strip("_")

    if not column:
        column = "column"

    if column[0].isdigit():
        column = "column_" + column

    return column


# ============================================================
# CLEAN COLUMNS
# ============================================================

def clean_columns(columns):

    cleaned = []

    used = {}

    for column in columns:

        name = clean_column_name(
            column
        )

        if name not in used:

            used[name] = 0

            cleaned.append(
                name
            )

        else:

            used[name] += 1

            new_name = (
                f"{name}_{used[name]}"
            )

            cleaned.append(
                new_name
            )

    return cleaned


# ============================================================
# DETERMINE POSTGRESQL TYPE
# ============================================================

def get_sql_type(series):

    dtype = series.dtype

    if pd.api.types.is_integer_dtype(
        dtype
    ):

        return "BIGINT"

    if pd.api.types.is_float_dtype(
        dtype
    ):

        return "DOUBLE PRECISION"

    if pd.api.types.is_bool_dtype(
        dtype
    ):

        return "BOOLEAN"

    if pd.api.types.is_datetime64_any_dtype(
        dtype
    ):

        return "TIMESTAMP"

    return "TEXT"


# ============================================================
# CREATE TABLE
# ============================================================

def create_table_from_dataframe(
    dataframe,
    table_name
):

    columns_sql = []

    for column in dataframe.columns:

        sql_type = get_sql_type(
            dataframe[column]
        )

        columns_sql.append(
            f'"{column}" {sql_type}'
        )

    query = f"""
    CREATE TABLE IF NOT EXISTS
    "{table_name}"
    (
        {", ".join(columns_sql)}
    );
    """

    with engine.connect() as conn:

        conn.execute(
            text(query)
        )

        conn.commit()


# ============================================================
# INSERT DATA
# ============================================================

def insert_dataframe(
    dataframe,
    table_name
):

    if dataframe.empty:

        return 0

    dataframe.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False,
        method="multi"
    )

    return len(
        dataframe
    )


# ============================================================
# IMPORT ONE EXCEL SHEET
# ============================================================

def import_excel_sheet(
    file_path,
    sheet_name,
    table_name
):

    dataframe = pd.read_excel(
        file_path,
        sheet_name=sheet_name
    )

    dataframe = dataframe.dropna(
        how="all"
    )

    dataframe = dataframe.dropna(
        axis=1,
        how="all"
    )

    if dataframe.empty:

        return {
            "table_name": table_name,
            "rows": 0,
            "columns": 0
        }

    dataframe.columns = clean_columns(
        dataframe.columns
    )

    create_table_from_dataframe(
        dataframe,
        table_name
    )

    rows = insert_dataframe(
        dataframe,
        table_name
    )

    return {
        "table_name": table_name,
        "rows": rows,
        "columns": len(
            dataframe.columns
        )
    }


# ============================================================
# REGISTER EXCEL TABLES
# ============================================================

def register_excel_tables(
    user_email,
    filename,
    import_results
):

    if not user_email:

        return []

    from workspace import save_workspace

    registered = []

    for result in import_results:

        table_name = result.get(
            "table_name"
        )

        if not table_name:

            continue

        if result.get("error"):

            continue

        try:

            save_workspace(
                user_email,
                filename,
                table_name
            )

            registered.append(
                table_name
            )

        except Exception as e:

            print(
                "Workspace registration error:",
                e
            )

    return registered
# ============================================================
# IMPORT COMPLETE EXCEL WORKBOOK
# ============================================================

def import_excel_workbook(
    file_path,
    filename,
    user_email=None
):

    excel = pd.ExcelFile(
        file_path
    )

    results = []

    base_name = clean_table_name(
        filename
    )

    for sheet_name in excel.sheet_names:

        clean_sheet = clean_table_name(
            sheet_name
        )

        table_name = (
            f"{base_name}_{clean_sheet}"
        )

        table_name = table_name[:60]

        try:

            result = import_excel_sheet(
                file_path,
                sheet_name,
                table_name
            )

            result["sheet_name"] = (
                sheet_name
            )

            result["filename"] = (
                filename
            )

            result["user_email"] = (
                user_email
            )

            results.append(
                result
            )

        except Exception as e:

            results.append(
                {
                    "table_name": table_name,
                    "sheet_name": sheet_name,
                    "filename": filename,
                    "user_email": user_email,
                    "rows": 0,
                    "columns": 0,
                    "error": str(e)
                }
            )

    excel.close()

    # ========================================================
    # REGISTER TABLES FOR USER
    # ========================================================

    if user_email:

        register_excel_tables(
            user_email,
            filename,
            results
        )

    return results