import pandas as pd

from chart_generator import (
    create_chart,
    detect_chart_type,
    detect_chart_columns
)

data = pd.DataFrame({
    "category": ["Furniture", "Electronics"],
    "total_revenue": [115000, 270000]
})

question = "What is our revenue by category?"

chart_type = detect_chart_type(data)

print(f"Chart type: {chart_type}")

x_column, y_column = detect_chart_columns(data)

print(f"X column: {x_column}")
print(f"Y column: {y_column}")

figure = create_chart(
    result=data,
    chart_type=chart_type,
    title="Revenue by Category",
    x_column=x_column,
    y_column=y_column
)

print("Chart created successfully:", figure is not None)
