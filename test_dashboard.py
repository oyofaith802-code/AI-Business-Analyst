from dashboard_agent import get_dashboard_metrics


metrics = get_dashboard_metrics(
    "olist_orders_dataset"
)

print(metrics)