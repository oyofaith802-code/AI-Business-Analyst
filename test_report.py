from report_agent import generate_report


metrics = {
    "Rows": 99441
}


insights = """
Sales performance is stable.
Delivery success rate is high.
"""


report = generate_report(
    "olist_orders_dataset",
    metrics,
    insights
)


print(report)