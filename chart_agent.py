import pandas as pd
import matplotlib.pyplot as plt
import io


def create_chart(result, question):

    # =====================================================
    # CHECK RESULT
    # =====================================================

    if result is None:
        return None

    if len(result) == 0:
        return None

    # =====================================================
    # CONVERT DATABASE RESULT TO DATAFRAME
    # =====================================================

    try:

        if isinstance(result, pd.DataFrame):

            df = result.copy()

        else:

            df = pd.DataFrame(
                result
            )

    except Exception:

        return None

    # =====================================================
    # CHECK DATA
    # =====================================================

    if df.empty:
        return None

    if len(df.columns) < 2:
        return None

    # =====================================================
    # CLEAN COLUMN NAMES
    # =====================================================

    df.columns = [
        str(column)
        for column in df.columns
    ]

    # =====================================================
    # IDENTIFY X AND Y COLUMNS
    # =====================================================

    x_column = df.columns[0]
    y_column = df.columns[1]

    # =====================================================
    # CONVERT Y COLUMN TO NUMERIC
    # =====================================================

    try:

        df[y_column] = pd.to_numeric(
            df[y_column],
            errors="coerce"
        )

    except Exception:

        return None

    df = df.dropna(
        subset=[y_column]
    )

    if df.empty:
        return None

    # =====================================================
    # CREATE FIGURE
    # =====================================================

    fig, ax = plt.subplots(
        figsize=(10, 5)
    )

    # =====================================================
    # DETERMINE CHART TYPE
    # =====================================================

    question_lower = question.lower()

    # -----------------------------------------------------
    # MONTHLY / TIME SERIES
    # -----------------------------------------------------

    if (
        "month" in question_lower
        or "monthly" in question_lower
        or "year" in question_lower
        or "yearly" in question_lower
        or "daily" in question_lower
        or "weekly" in question_lower
        or "over time" in question_lower
        or "trend" in question_lower
    ):

        ax.plot(
            df[x_column],
            df[y_column],
            marker="o"
        )

        ax.set_xlabel(
            x_column.replace("_", " ").title()
        )

        ax.set_ylabel(
            y_column.replace("_", " ").title()
        )

        ax.set_title(
            question.title()
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )

    # -----------------------------------------------------
    # BAR CHART
    # -----------------------------------------------------

    else:

        ax.bar(
            df[x_column].astype(str),
            df[y_column]
        )

        ax.set_xlabel(
            x_column.replace("_", " ").title()
        )

        ax.set_ylabel(
            y_column.replace("_", " ").title()
        )

        ax.set_title(
            question.title()
        )

        plt.xticks(
            rotation=45,
            ha="right"
        )

    # =====================================================
    # LAYOUT
    # =====================================================

    plt.tight_layout()

    # =====================================================
    # SAVE FIGURE TO MEMORY
    # =====================================================

    image_buffer = io.BytesIO()

    plt.savefig(
        image_buffer,
        format="png",
        bbox_inches="tight"
    )

    plt.close(fig)

    image_buffer.seek(0)

    return image_buffer