import pandas as pd

from chart_generator import (
    create_chart,
    choose_chart_type,
    detect_chart_columns
)


# ============================================================
# TEST DATA
# ============================================================

data = pd.DataFrame(
    {
        "category": [
            "Furniture",
            "Electronics"
        ],

        "total_revenue": [
            115000,
            270000
        ]
    }
)


# ============================================================
# BUSINESS QUESTION
# ============================================================

question = "What is our revenue by category?"


# ============================================================
# DETECT CHART TYPE
# ============================================================

chart_type = choose_chart_type(
    question,
    data
)

print(
    f"Chart type: {chart_type}"
)


# ============================================================
# DETECT COLUMNS
# ============================================================

x_column, y_column = detect_chart_columns(
    data
)

print(
    f"X column: {x_column}"
)

print(
    f"Y column: {y_column}"
)


# ============================================================
# CREATE CHART
# ============================================================

figure = create_chart(
    result=data,
    chart_type=chart_type,
    title="Revenue by Category",
    x_column=x_column,
    y_column=y_column
)


# ============================================================
# DISPLAY
# ============================================================

if figure:

    print(
        "✅ Chart created successfully."
    )

    figure.show()

else:

    print(
        "❌ Chart creation failed."
    )